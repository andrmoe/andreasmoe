"""Exploratory Bayesian synthesis of trusted AI-control growth.

Run: python ai_control.py {fit,refresh,expand,test} [options]
Dependencies: numpy, scipy, matplotlib. No network access at inference time.
All probabilities are conditional on the transport and frontier-gap priors.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import datetime
import re
import sys
import unittest
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import expit, log_ndtr, ndtri_exp

ROOT = Path(__file__).resolve().parent


def logit(p):
    p = np.clip(p, 0.0001, 0.9999)
    return np.log(p / (1 - p))


def truncated_normal(rng, mean, sd, lower=-np.inf, upper=np.inf):
    """Stable inverse-CDF draws, including extreme one-sided truncation."""
    mean, sd, lower, upper = np.broadcast_arrays(mean, sd, lower, upper)
    lo = (lower - mean) / sd
    hi = (upper - mean) / sd
    # Reflect positive truncation to the negative tail, avoiding 1-CDF cancellation.
    reflect = lo > 0
    a = np.where(reflect, -hi, lo)
    b = np.where(reflect, -lo, hi)
    log_b = log_ndtr(b)
    ratio = np.exp(log_ndtr(a) - log_b)
    log_p = log_b + np.log(ratio + (1 - ratio) * rng.uniform(size=mean.shape))
    z = ndtri_exp(log_p)
    z = np.where(reflect, -z, z)
    return np.clip(mean + sd * z, lower, upper)


def truncated_scalar(rng, mean, sd, lower, upper):
    lo, hi = (lower - mean) / sd, (upper - mean) / sd
    reflect = lo > 0
    a, b = (-hi, -lo) if reflect else (lo, hi)
    lb = log_ndtr(b)
    ratio = math.exp(log_ndtr(a) - lb)
    z = ndtri_exp(lb + math.log(ratio + (1 - ratio) * rng.random()))
    return min(upper, max(lower, mean + sd * (-z if reflect else z)))


def model_observations(data):
    """Project source records onto attacker, trusted monitor and protocol only.

    Preserve every outcome, but never use an untrusted helper's identity,
    capability or condition as a feature or a separate protocol candidate.
    """
    observations = []
    for original in data["observations"]:
        o = original.copy()
        if o["study"] == "2606.11998":
            if o["protocol"] == "bootstrap-trusted-only":
                pass
            elif o["protocol"] in {"bootstrap-helper-only", "bootstrap-direct-monitor"}:
                # These are direct-monitor evaluations. The evaluated monitor
                # occupies M under the same hypothetical honesty guarantee.
                o["protocol"] = "bootstrap-direct-monitor"
            else:
                o["protocol"] = o.get("protocol_variant", "bootstrapped-monitoring")
            o.pop("condition_effect", None)
            o.pop("evaluation_group", None)
            # Pool heterogeneous outcomes without inventing helper-specific
            # explanatory effects. This extra residual scale is an assumption.
            o["logit_sd"] = math.hypot(o["logit_sd"], 1.5)
        observations.append(o)
    return observations


def build_design(data, transport_sd, progress_sd, gap_sd=1.0, slope_sd=0.35, drift_sd=0.5):
    obs = model_observations(data)
    names = ["intercept", "protocol_progress", "monitor_response", "attacker_response"]
    means = [0.0, 0.0, 0.6, 0.6]
    sds = [4.0, progress_sd, 0.8, 0.8]
    positive = [False, True, True, True]

    def add(name, sd, nonnegative=False):
        if name not in names:
            names.append(name)
            means.append(0.0)
            sds.append(sd)
            positive.append(nonnegative)
        return names.index(name)

    # Shared effects prevent the many cells of one paper becoming independent
    # evidence about a historical trend. Bounds retain missing outcome information.
    rows = []
    for o in obs:
        row = {0: 1.0, 1: o["year"], 2: o["ln_monitor"] if o.get("candidate_eligible", True) else 0., 3: -o["ln_attacker"]}
        row[add("study:" + o["study"], transport_sd)] = 1.0
        row[add("monitor-slope:" + o["study"], slope_sd)] = o["ln_monitor"] if o.get("candidate_eligible", True) else 0.
        if o.get("evaluation_group"):
            row[add("evaluation:" + o["evaluation_group"], 1.0)] = 1.0
        row[add("attacker-slope:" + o["study"], slope_sd)] = -o["ln_attacker"]
        # Benchmark difficulty/elicitation may change systematically over time.
        # It is not identified separately from progress; expose that uncertainty.
        row[add("benchmark_drift", drift_sd)] = o["year"]
        row[add("gap:" + o["protocol"], gap_sd, True)] = -1.0
        if o.get("ease"):
            row[add("ease:" + o["ease"], 1.5, True)] = 1.0
        if o.get("extra_attack"):
            row[add("extra:" + o["extra_attack"], 2.0, True)] = -1.0
        if o["metric"] != "safety":
            row[add("metric:" + o["metric"], transport_sd)] = 1.0
        if o.get("model_effect"):
            row[add("model:" + o["model_effect"], 1.0)] = 1.0
        if o.get("resource_excess"):
            row[add("resource:" + o["protocol"], 1.5, True)] = o["resource_excess"]
        rows.append(row)
    x = np.zeros((len(obs), len(names)))
    for i, row in enumerate(rows):
        for j, value in row.items():
            x[i, j] = value
    noise = np.array([o["logit_sd"] for o in obs])
    lower = np.array([logit(o["lower"]) if "lower" in o else -np.inf for o in obs])
    upper = np.array([logit(o["upper"]) if "upper" in o else np.inf for o in obs])
    y = np.array([logit(o.get("value", o.get("upper", o.get("lower", 0.5)))) for o in obs])
    censored = np.array(["value" not in o for o in obs])
    return x, y, noise, lower, upper, censored, names, np.array(means), np.array(sds), np.array(positive)


def sample(data, transport_sd, progress_sd, draws, burn, chains, gap_sd=1.0, slope_sd=0.35, drift_sd=0.5):
    x, y0, noise, lower, upper, censored, names, prior_mean, prior_sd, positive = build_design(
        data, transport_sd, progress_sd, gap_sd, slope_sd, drift_sd
    )
    # Collapse unconstrained Gaussian effects exactly. This avoids the very slow
    # mixing caused by alternating a historical slope with paper intercepts.
    constrained = np.flatnonzero(positive)
    gaussian = np.flatnonzero(~positive)
    xc, xu = x[:, constrained], x[:, gaussian]
    covariance = np.diag(noise**2) + (xu * prior_sd[gaussian]**2) @ xu.T
    inv_cov = np.linalg.inv(covariance)
    score_loading = xc.T @ inv_cov
    precision = score_loading @ xc + np.diag(1 / prior_sd[constrained]**2)
    sd = 1 / np.sqrt(precision.diagonal())
    prior_h = prior_mean[constrained] / prior_sd[constrained]**2
    cmean = prior_mean[constrained]
    intercept_loading = prior_sd[0]**2 * x[:, 0] @ inv_cov
    intercept_sd = math.sqrt(max(0, prior_sd[0]**2 - intercept_loading @ x[:, 0] * prior_sd[0]**2))
    censored_indices = np.flatnonzero(censored)
    censor_sd = 1 / np.sqrt(inv_cov.diagonal())
    output_names = [names[0]] + [names[j] for j in constrained]
    samples = []
    predictions = []
    for chain in range(chains):
        rng = np.random.default_rng(20261027 + chain * 191)
        theta = cmean.copy()
        theta[:3] = rng.uniform(0.1, 1.0, 3)
        y = y0.copy()
        kept = []
        # Gibbs conditionals are exact for this Gaussian working likelihood.
        y_sum = np.zeros_like(y)
        for step in range(burn + draws):
            if censored.any():
                pred = xc @ theta
                censor_residual = inv_cov @ (y - pred)
                for j in censored_indices:
                    mean = y[j] - censor_residual[j] * censor_sd[j]**2
                    new = truncated_scalar(rng, mean, censor_sd[j], lower[j], upper[j])
                    delta = new - y[j]
                    y[j] = new
                    censor_residual += inv_cov[:, j] * delta
            h = score_loading @ y + prior_h
            residual = h - precision @ theta
            uniforms = rng.uniform(size=len(theta))
            for j in range(len(theta)):
                mean = theta[j] + residual[j] * sd[j] ** 2
                # P(Z > -mean/sd) = Phi(mean/sd).
                new = max(0.0, mean - sd[j] * ndtri_exp(math.log(uniforms[j]) + log_ndtr(mean / sd[j])))
                delta = new - theta[j]
                theta[j] = new
                residual -= precision[:, j] * delta
            if step >= burn:
                intercept = intercept_loading @ (y - xc @ theta) + intercept_sd * rng.normal()
                kept.append(np.r_[intercept, theta])
                y_sum += y
        kept = np.array(kept)
        samples.append(kept)
        residual_mean = y_sum / draws - xc @ kept[:, 1:].mean(axis=0)
        gaussian_mean = prior_sd[gaussian]**2 * (xu.T @ inv_cov @ residual_mean)
        predictions.append(xc @ kept[:, 1:].mean(axis=0) + xu @ gaussian_mean)
    return np.array(samples), output_names, np.mean(predictions, axis=0)


def split_rhat(chains):
    n = chains.shape[1] // 2
    a = np.concatenate([chains[:, :n], chains[:, -n:]], axis=0)
    w = a.var(axis=1, ddof=1).mean(axis=0)
    b = n * a.mean(axis=1).var(axis=0, ddof=1)
    return np.sqrt(((n - 1) / n * w + b / n) / w)


def ess(chains):
    """Conservative autocorrelation ESS for displayed growth coefficients."""
    m, n, d = chains.shape
    out = []
    for j in range(d):
        a = chains[:, :, j] - chains[:, :, j].mean(axis=1, keepdims=True)
        f = np.fft.rfft(a, n=2 * n, axis=1)
        ac = np.fft.irfft(f * np.conjugate(f), axis=1)[:, :n]
        ac /= np.arange(n, 0, -1)
        ac = ac.mean(axis=0)
        ac /= ac[0]
        total = 0.0
        for k in range(1, n - 1, 2):
            pair = ac[k] + ac[k + 1]
            if pair < 0:
                break
            total += pair
        out.append(min(m * n, m * n / (1 + 2 * total)))
    return np.array(out)


def frontier_fit(data):
    # Release-date records, not every model, and no repeatedly sampled daily points.
    frontier = []
    record = 0
    for m in sorted(data["frontier"], key=lambda z: z["year"]):
        if m["p50"] > record:
            frontier.append(m)
            record = m["p50"]
    x = np.array([m["year"] for m in frontier])
    y = np.log([m["p50"] for m in frontier])
    fitted = np.polyfit(x, y, 1)
    # Trend-window/model uncertainty is much larger than regression sampling SE.
    late = x >= 1.0
    recent = np.polyfit(x[late], y[late], 1)[0]
    published = data["published_frontier_trend"]
    gf = published["annual_log_growth"]
    return {"annual_log_growth": gf, "recent_annual_log_growth": float(recent),
            "record_fit_annual_log_growth": float(fitted[0]), "source": published["source"],
            "doubling_months": float(12 * math.log(2) / gf), "trend_sd_assumption": 0.35,
            "record_models": [m["name"] for m in frontier]}


def protocol_candidates(data):
    candidates = {}
    for o in model_observations(data):
        if not o.get("candidate_eligible", True) or not o.get("leader_eligible", True):
            continue
        if o["protocol"] not in candidates or o["date"] < candidates[o["protocol"]]["date"]:
            candidates[o["protocol"]] = {"id": o["protocol"], "date": o["date"], "year": o["year"], "study": o["study"]}
    labels = {v["id"]: v["label"] for v in data.get("variants", [])}
    for c in candidates.values():
        c["label"] = labels.get(c["id"], c["id"])
    return sorted(candidates.values(), key=lambda p: (p["date"], p["id"]))


def summarize(samples, growth, monitor_fraction, attack_drift=0, candidates=None, names=None):
    flat = samples.reshape(-1, samples.shape[-1])
    rng = np.random.default_rng(314159)
    gf = np.maximum(0.01, rng.normal(growth["annual_log_growth"], growth["trend_sd_assumption"], len(flat)))
    gp, bm, ba = flat[:, 1], flat[:, 2], flat[:, 3]
    if candidates is not None:
        # Methods are frozen at their publication-date effectiveness, then reused.
        # Changing the trusted monitor is a separate term. Maximize separately in
        # each posterior draw, rather than selecting a point-estimate winner.
        score = np.column_stack([gp * c["year"] - flat[:, names.index("gap:" + c["id"])] for c in candidates])
        first = min(c["year"] for c in candidates)
        last = max(c["year"] for c in candidates)
        first_score = score[:, [i for i, c in enumerate(candidates) if c["year"] == first]].max(axis=1)
        gp = (score.max(axis=1) - first_score) / (last - first)
    margin = gp + bm * monitor_fraction * gf - ba * gf - attack_drift
    relative_growth = margin / ba
    # The sign is the central estimand; tiny ba produces unstable time-horizon ratios.
    return {"p_control_faster": float(np.mean(margin > 0)),
            "margin_logit_per_year_90": np.quantile(margin, [.05, .5, .95]).tolist(),
            "relative_log_horizon_growth_90": np.quantile(relative_growth, [.05, .5, .95]).tolist()}


def fit_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--draws", type=int, default=2500)
    parser.add_argument("--burn", type=int, default=2500)
    parser.add_argument("--chains", type=int, default=4)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    data = json.loads((ROOT / "evidence.json").read_text())
    validate_evidence(data)
    growth = frontier_fit(data)
    results = {"interpretation": "Conditional sensitivity analysis; not a calibrated probability for all real-world control.",
               "model_scope": "Attacker capability, trusted-monitor capability and protocol outcomes only; no untrusted-helper features or helper-specific candidates.",
               "sampling": {"draws_per_chain": args.draws, "burn_per_chain": args.burn, "chains": args.chains},
               "frontier": growth, "observation_count": len(data["observations"]),
               "source_count": len(data["sources"]), "settings": []}
    from concurrent.futures import ProcessPoolExecutor
    pool = ProcessPoolExecutor(max_workers=args.workers)
    fits = {(t, p): pool.submit(sample, data, t, p, args.draws, args.burn, args.chains)
            for t in [.75, 1.5, 3.] for p in [.5, 1., 2.]}
    stress_specs = [(1.5, 1., 1., .35, 1.5), (1.5, 1., 1., .75, .5), (3., 2., 2., .75, 1.5)]
    stress_fits = [pool.submit(sample, data, t, p, args.draws, args.burn, args.chains, g, s, d)
                  for t, p, g, s, d in stress_specs]
    baseline = None
    for transport in [.75, 1.5, 3.0]:
        for progress in [.5, 1.0, 2.0]:
            chains, names, prediction = fits[(transport, progress)].result()
            rh = split_rhat(chains[:, :, :4])
            effective = ess(chains[:, :, :4])
            row = {"transport_sd": transport, "protocol_progress_prior_sd": progress,
                   "rhat": dict(zip(names[:4], rh.tolist())), "ess": dict(zip(names[:4], effective.tolist())),
                   "coefficients_90": {name: np.quantile(chains[:, :, j], [.05, .5, .95]).tolist() for j, name in enumerate(names[:4])},
                   "trust_scenarios": {str(f): summarize(chains, growth, f, candidates=protocol_candidates(data), names=names) for f in [0.0, 0.5, 1.0]},
                   "underlying_trust_scenarios": {str(f): summarize(chains, growth, f) for f in [0.0, 0.5, 1.0]}}
            results["settings"].append(row)
            print(json.dumps({"transport": transport, "progress": progress,
                              "p_faster": {k: round(v["p_control_faster"], 3) for k, v in row["trust_scenarios"].items()},
                              "max_rhat": round(float(rh.max()), 3), "min_ess": round(float(effective.min()))}), flush=True)
            if transport == 1.5 and progress == 1.0:
                baseline = chains
                results["baseline_diagnostics"] = {"all_parameters_max_rhat": float(split_rhat(chains).max()),
                                                   "all_parameters_min_ess": float(ess(chains).min())}
                results["baseline_observation_fit"] = [dict(id=o["id"], predicted_working_score=float(expit(p))) for o, p in zip(data["observations"], prediction)]
    pool.shutdown()
    assert baseline is not None
    results["baseline_attack_drift_sensitivity"] = {
        str(drift): {str(f): summarize(baseline, growth, f, drift, protocol_candidates(data), names) for f in [0., .5, 1.]}
        for drift in [0., .5, 1.]
    }
    results["structural_sensitivity"] = run_stress_cases(data, growth, args, stress_fits)
    results["diagnostics_pass"] = all(max(r["rhat"].values()) < 1.05 and min(r["ess"].values()) > 400 for r in results["settings"])
    results["diagnostics_pass"] &= all(r["max_rhat"] < 1.05 and r["min_ess"] > 400 for r in results["structural_sensitivity"])
    (ROOT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    np.savez_compressed(ROOT / "baseline_draws.npz", draws=baseline, names=names)
    draw_figure(results)
    export_page_data(data, results, baseline)


def run_stress_cases(data, growth, args, fits=None):
    out = []
    cases = [
        ("More systematic change in benchmark difficulty", 1.5, 1., 1., .35, 1.5),
        ("Less transferable capability slopes", 1.5, 1., 1., .75, .5),
        ("Weak identification", 3., 2., 2., .75, 1.5),
    ]
    for index, (label, transport, progress, gap, slope, drift) in enumerate(cases):
        samples, names, _ = fits[index].result() if fits is not None else sample(data, transport, progress, args.draws, args.burn, args.chains, gap, slope, drift)
        rhat = split_rhat(samples[:, :, :4])
        effective = ess(samples[:, :, :4])
        out.append({"name": label, "transport_sd": transport, "progress_sd": progress,
                    "gap_sd": gap, "slope_sd": slope, "drift_sd": drift,
                    "max_rhat": float(rhat.max()), "min_ess": float(effective.min()),
                    "trust_scenarios": {str(f): summarize(samples, growth, f, candidates=protocol_candidates(data), names=names) for f in [0., .5, 1.]}})
        print(json.dumps({"structural_sensitivity": label, "p_faster": {k: round(v["p_control_faster"], 3) for k, v in out[-1]["trust_scenarios"].items()}}), flush=True)
    return out


def validate_evidence(data):
    obs = data["observations"]
    assert len({o["id"] for o in obs}) == len(obs), "Duplicate observation IDs"
    known = {s["id"] for s in data["sources"]}
    for o in obs:
        assert o["study"] in known
        for key in ["value", "lower", "upper"]:
            if key in o:
                assert 0 < o[key] < 1, (o["id"], key)
        assert "value" in o or "lower" in o or "upper" in o
        assert o["logit_sd"] > 0
        if "lower" in o and "upper" in o:
            assert o["lower"] < o["upper"]


def export_page_data(data, results, baseline, names=None):
    """Keep the web visualization reproducible from the same fitted posterior."""
    flat = baseline.reshape(-1, baseline.shape[-1])
    rng = np.random.default_rng(314159)
    gf = np.maximum(.01, rng.normal(results["frontier"]["annual_log_growth"], .35, len(flat)))
    chosen = np.random.default_rng(20261027).choice(len(flat), min(2000, len(flat)), replace=False)
    posterior = np.column_stack([flat[:, :4], gf])[chosen]
    if names is None:
        names = list(np.load(ROOT / "baseline_draws.npz")["names"])
    candidates = protocol_candidates(data)
    observations_for_model = model_observations(data)
    for candidate in candidates:
        observations = [o for o in observations_for_model if o["protocol"] == candidate["id"]]
        candidate["testedAttackers"] = sorted({o["attacker"] for o in observations if not o.get("extra_attack")})
        candidate["testedMonitors"] = sorted({o["monitor"] for o in observations})
    capabilities = {}
    measured = {m["name"]: m for m in data["frontier_plot"] if not m["estimated"]}
    for name, capability in {**data["models"], **data.get("unknown_models", {})}.items():
        if name in measured:
            m = measured[name]
            capabilities[name] = {"p50": m["p50"], "lo": m["lo"], "hi": m["hi"], "estimated": False, "rangeLabel": "METR 95% CI"}
        else:
            capabilities[name] = {"p50": capability["p50"], "estimated": True,
                                  "lo": capability["p50"] * math.exp(-1.645 * capability["log_sd"]),
                                  "hi": capability["p50"] * math.exp(1.645 * capability["log_sd"]),
                                  "rangeLabel": "90% working capability range, from ECI conversion and modeling uncertainty"}
    aliases = {"Opus 4.5": "Claude Opus 4.5", "GPT-4.1 Mini": "GPT-4.1 mini",
               "GPT-4o Mini": "GPT-4o mini", "GPT-4 Turbo": "GPT-4 Turbo (Nov 2023)"}
    for alias, canonical in aliases.items():
        capabilities[alias] = capabilities[canonical]
    for name in data.get("unknown_models", {}):
        capabilities[name]["unplaced"] = True
    gaps = flat[chosen][:, [names.index("gap:" + c["id"]) for c in candidates]]
    counts = {s["id"]: sum(o["study"] == s["id"] for o in data["observations"]) for s in data["sources"]}
    cases = []
    for case in results["settings"]:
        cases.append({"name": f'Transport {case["transport_sd"]}; progress prior {case["protocol_progress_prior_sd"]}',
                      "scenarios": case["trust_scenarios"]})
    for case in results["structural_sensitivity"]:
        cases.append({"name": case["name"], "scenarios": case["trust_scenarios"]})
    reference = next(s for s in results["settings"] if s["transport_sd"] == 1.5 and s["protocol_progress_prior_sd"] == 1.)
    page = {"asOf": "2026-10-27", "origin": "2023-12-12", "referenceDate": "2026-09-24",
            "evidenceEnd": "2026-09-24", "chartEnd": "2026-10-27", "posterior": np.round(posterior, 7).tolist(),
            "protocols": candidates, "gaps": np.round(gaps, 7).tolist(),
            "testedCapabilities": capabilities,
            "frontier": data["frontier_plot"], "frontierGrowth": results["frontier"],
            "scenarios": reference["trust_scenarios"], "assumptions": cases,
            "attackDrift": results["baseline_attack_drift_sensitivity"],
            "sources": [dict(s, count=counts[s["id"]]) for s in data["sources"]],
            "variants": data.get("variants", []), "observations": observations_for_model, "modelScope": results["model_scope"], "diagnosticsPass": results["diagnostics_pass"]}
    target = ROOT.parents[1] / "ai_control_growth.js"
    marker = "// END GENERATED CONTROL DATA\n"
    renderer = target.read_text().split(marker, 1)[1]
    target.write_text("// BEGIN GENERATED CONTROL DATA — regenerate with analysis/ai_control_growth/ai_control.py\n" +
                      "window.AI_CONTROL_GROWTH = " + json.dumps(page, separators=(",", ":")) + ";\n" + marker + renderer)



def draw_figure(results):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.5), constrained_layout=True, sharey=True)
    for ax, fraction, title in zip(axs, ["0.0", "0.5", "1.0"],
                                   ["Fixed trusted model", "Trusted capability grows half as fast", "Trusted capability keeps a fixed relative gap"]):
        matrix = np.array([[next(r for r in results["settings"] if r["transport_sd"] == tr and r["protocol_progress_prior_sd"] == pr)
                            ["trust_scenarios"][fraction]["p_control_faster"] for pr in [.5, 1., 2.]] for tr in [.75, 1.5, 3.]])
        ax.imshow(matrix, vmin=0, vmax=1, cmap="RdBu", aspect="auto")
        for i in range(3):
            for j in range(3):
                v = matrix[i, j]
                ax.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=15, color="white" if v < .2 or v > .8 else "black")
        ax.set_xticks(range(3), ["0.5", "1", "2"])
        ax.set_yticks(range(3), ["0.75", "1.5", "3"])
        ax.set_xlabel("Protocol progress prior scale (log-odds/year)")
        ax.set_title(title, fontsize=10)
    axs[0].set_ylabel("Uncertainty transporting studies (log-odds)")
    fig.suptitle("Probability control capability grows faster than frontier capability\nConditional on this model and its priors; differences across cells are substantive", fontsize=13)
    fig.savefig(ROOT / "growth_sensitivity.png", dpi=180)
    fig.savefig(ROOT / "growth_sensitivity.svg")
    plt.close(fig)




# Primary-paper evidence expansion
ORIGIN=datetime.date(2023,12,12)
DATES={'2312.06942':'2023-12-12','2504.10374':'2025-04-14','2510.09462':'2025-10-10','2511.02997':'2025-11-04','2604.15384':'2026-04-16','2605.26047':'2026-05-25','2606.06529':'2026-06-03','2606.11998':'2026-06-10','2609.19587v2':'2026-09-17','2605.09684':'2026-05-10','2609.30217':'2026-09-24','2602.20628':'2026-09-21','2504.18530':'2025-04-25','2512.22154':'2025-12-26'}
ALIASES={'Opus 4.5':'Claude Opus 4.5','GPT-4.1 Mini':'GPT-4.1 mini','GPT-4o Mini':'GPT-4o mini','GPT-4 Turbo':'GPT-4 Turbo (Nov 2023)','Claude-4.5-Opus':'Claude Opus 4.5','Sonnet 4':'Claude Sonnet 4','Sonnet 4.0':'Claude Sonnet 4','Sonnet 4.5':'Claude Sonnet 4.5','GPT-OSS-120B':'gpt-oss-120b','GPT-5 Mini':'GPT-5 mini'}

def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def num(s):
 m=re.search(r'[-+]?\d+(?:\.\d+)?',str(s));return float(m[0]) if m else None

def table_rows(table):
 """Expand row/column spans before reading model or result columns."""
 carry={};out=[]
 for i,row in enumerate(table['rows']):
  cells={j:v for j,(v,end) in carry.items() if end>i};j=0
  for c in row:
   while j in cells:j+=1
   for k in range(int(c.get('colspan',1))):
    cells[j+k]=c['text']
    if int(c.get('rowspan',1))>1:carry[j+k]=(c['text'],i+int(c['rowspan']))
   j+=int(c.get('colspan',1))
  out.append([cells.get(j,'') for j in range(max(cells,default=-1)+1)])
 return out

class Expansion:
 def __init__(self,cache):
  self.cache=Path(cache);self.data=json.loads((ROOT/'evidence_base.json').read_text());self.obs=self.data['observations'];self.variants={};self.review=[];self.data.setdefault('unknown_models',{})
 def source(self,pid):return json.loads((self.cache/(pid+'.json')).read_text())
 def table(self,pid,id):return next(t for t in self.source(pid)['tables'] if t['id']==id)
 def rows(self,pid,id):return table_rows(self.table(pid,id))
 def capability(self,name):
  canonical=ALIASES.get(name,name);c=self.data['models'].get(canonical)
  if c:return canonical,math.log(c['p50']/4),c['log_sd']
  self.data['unknown_models'].setdefault(canonical,{'p50':60,'log_sd':2.5,'meaning':'Unmeasured covariate; the center is a working convention, not an empirical estimate.'})
  return canonical,math.log(60/4),2.5
 def register(self,pid,id,label,location,kind='protocol',notes='',cost='',eligible=True):
  self.variants.setdefault(id,dict(id=id,study=pid,label=label,locations=[],kind=kind,notes=notes,cost=cost,candidate_eligible=eligible,observation_ids=[]))
  v=self.variants[id]
  if location not in v['locations']:v['locations'].append(location)
  return v
 def add(self,pid,protocol,label,location,att,mon,value=None,lower=None,upper=None,condition='',metric='safety',usefulness=None,fpr=None,sd=.55,cost='',notes='',kind='protocol',eligible=True,context=None):
  att,la,ae=self.capability(att);mon,lm,me=self.capability(mon)
  v=self.register(pid,protocol,label,location,kind,notes,cost,eligible)
  oid='expanded-'+slug(pid+'-'+protocol+'-'+condition+'-'+att+'-'+mon+'-'+location)
  stem=oid;replicate=1
  while any(o['id']==oid for o in self.obs):
   replicate+=1;oid=stem+'-replicate-'+str(replicate)
  o=dict(id=oid,study=pid,date=DATES[pid],year=(datetime.date.fromisoformat(DATES[pid])-ORIGIN).days/365.25,
   attacker=att,monitor=mon,ln_attacker=la,ln_monitor=lm,protocol=protocol,protocol_label=label,
   metric=metric,logit_sd=math.sqrt(sd*sd+(.6*ae)**2+(.6*me)**2),condition=condition,
   source_location=location,candidate_eligible=eligible,detail=f'{location}. {condition}. {notes}'.strip())
  if value is not None:
   o['reported_value']=value;o['value']=max(.005,min(.995,value))
   if value in [0,1]:o['detail']+=' Boundary point regularized to 0.5–99.5% for the working likelihood; not a population guarantee.'
  if lower is not None:o['lower']=max(.0001,min(.9999,lower))
  if upper is not None:o['upper']=max(.0001,min(.9999,upper))
  if usefulness is not None:
   o['usefulness']=usefulness;o['resource_excess']=max(0,.95-usefulness)/.25
  if fpr is not None:o['false_positive_or_audit_budget']=fpr
  if cost:o['cost_notes']=cost
  if context:o['evaluation_group']=pid+':'+context
  if pid=='2606.11998' and protocol.startswith('bootstrapped-'):o['protocol_variant']=protocol
  self.obs.append(o);v['observation_ids'].append(oid)
 def drop(self,pid,reason):
  before=[o for o in self.obs if o['study']==pid]
  self.data.setdefault('superseded_summaries',[]).extend(dict(id=o['id'],reason=reason) for o in before)
  self.obs[:]=[o for o in self.obs if o['study']!=pid]
 def qualitative(self,pid,id,label,location,notes,kind='protocol',cost=''):
  self.register(pid,id,label,location,kind,notes,cost)
 def expand_greenblatt(self):
  p='2312.06942';self.drop(p,'Replaced by complete Table 7 and collusion/redaction tables.')
  for row in self.rows(p,'S3.T7')[1:]:
   label,s,u=row;id='greenblatt-'+slug(label)
   self.add(p,id,label,'Table 7','GPT-4','GPT-3.5 Turbo',num(s)/100,usefulness=num(u)/100,cost='Reported usefulness '+u,eligible=label!='Trusted model')
  for j,redaction in enumerate(['No redaction','Input redaction','Input and output redaction'],1):
   for row in self.rows(p,'S3.T6')[2:]:
    if row[0]=='Usefulness' or row[j]=='-':continue
    self.add(p,'greenblatt-untrusted-'+slug(redaction),'Monitoring with '+redaction,'Table 6','GPT-4','GPT-3.5 Turbo',num(row[j])/100,condition=row[0],usefulness=[.974,.972,.963][j-1],context='collusion:'+row[0])
  for row in self.rows(p,'S3.T5')[1:]:
   for j,label in enumerate(['Original synthetic tests','Hardened synthetic tests'],1):
    self.add(p,'greenblatt-'+slug(label),label,'Table 5','GPT-4','GPT-3.5 Turbo',float(row[j]),condition=row[0],sd=.8,context='synthetic-'+row[0])
  # Main-text trusted justification variant.
  self.qualitative(p,'greenblatt-monitor-justification','Trusted monitoring with model justification','Section 3.2.2','Reported not to improve plain monitoring; no scalar assigned.')
 def expand_ctrlz(self):
  p='2504.10374';self.drop(p,'Replaced by complete Tables 1–2 and monitoring baseline.')
  labels=['Defer to trusted','Defer to resample','Resample: incrimination in the present','Resample: three strikes','Resample: time travel']
  for row in self.rows(p,'S3.T1')[2:]:
   u=num(row[0])/100
   for j,label in enumerate(labels,1):self.add(p,'ctrlz-'+slug(label),label,'Table 1','GPT-4o mini','Llama 3.1 8B',num(row[j])/100,condition=f'{u:.0%} usefulness',usefulness=u,sd=1.5,notes='Attacks are assisted by human-provided templates; capability transport is uncertain.')
  for label,score in zip([labels[0],labels[1],labels[-1]],[.776,.911,.926]):
   self.add(p,'ctrlz-'+slug(label)+'-combined',label+' with additional monitoring','Table 2','GPT-4o mini','Llama 3.1 8B',score,usefulness=.95,sd=1.5,notes='Combined monitoring is a protocol variant; no separate helper capability enters the fit.')
  self.add(p,'ctrlz-trusted-monitoring','Trusted monitoring','Section 3.1.2','GPT-4o mini','Llama 3.1 8B',.418,sd=1.5)
  self.qualitative(p,'ctrlz-upfront-auditing','Upfront auditing','Section 3.1.1','Analytic baseline; audit budget sweep is shown in Figure 2.',kind='baseline')
  self.qualitative(p,'ctrlz-stop-after-edit','Stop-after-edit variant','Appendix I','Alternative deferral implementation; source curve retained for inspection.')
  self.qualitative(p,'ctrlz-audit-budget-sweep','Auditing budget variants: 0.3%, 1%, 3%','Appendix A, Figure 5','Budget sweeps of the listed protocols; main 1% table points extracted. Other curve points require digitization.',kind='operating-point sweep')
 def expand_auto(self):
  p='2609.19587v2';self.drop(p,'Replaced by all five protocols in Figure 3, full Table 3, and model-swap ablation.')
  ids=['auto-mode','guardian','guardian-strict','auto-mode-plus-plus','auto-mode-strict'];labels=['Auto Mode','Codex Guardian','Guardian strict','Auto Mode++','Auto Mode strict'];mon=['Claude Sonnet 5','GPT-5.6 Luna','GPT-5.6 Luna','Claude Opus 4.8','Claude Opus 4.8']
  matrix=[[.94,.95,.95,0,.02],[1,.37,.37,.23,.07],[.55,.70,.57,.04,.09],[.80,.98,.99,.29,.04],[.43,.72,.31,.02,0],[.54,.65,.62,.06,0]]
  cond=['Arena: monitor injection','Arena: multi-agent','Simulation: monitor injection','Simulation: compaction','Simulation: coverage gap','Simulation: policy failure']
  for j,(id,label,m) in enumerate(zip(ids,labels,mon)):
   cost='Highest latency: agentic review on every action; slower than interactive deployment.' if id=='auto-mode-strict' else 'All edits monitored.' if 'strict' in id or 'plus' in id else 'Production-style blocking monitor.'
   for i,c in enumerate(cond):self.add(p,id,label,'Figure 3','Claude Opus 5',m,1-matrix[i][j],condition=c,metric='blocked_episode',cost=cost,context=c,notes='One minus the attack-success percentage printed in the figure. Aggregate means are not counted again.')
  for row in self.rows(p,'A5.T3')[1:]:
   label,m,inj,multi=row
   if label:current=label
   if current=='no monitor':
    self.qualitative(p,'auto-no-monitor','No monitor','Table 3','14/14 multi-agent rogue deployments succeeded.',kind='baseline');continue
   idx={'auto mode':0,'guardian':1,'guardian strict':2,'auto mode ++':3,'auto mode strict':4}[current]
   monitor={'Sonnet 5':'Claude Sonnet 5','Opus 4.8':'Claude Opus 4.8','GPT 5.6 Luna':'GPT-5.6 Luna'}[m]
   for attack,value in [('Rogue deployment: injection',inj),('Rogue deployment: 20 agents',multi)]:
    if value=='–':continue
    successes,n=map(int,re.findall(r'\d+',value))
    self.add(p,ids[idx],labels[idx],'Table 3','Claude Opus 5',monitor,(n-successes+.5)/(n+1),condition=attack,metric='blocked_episode',sd=.8,context=attack,notes=f'{successes}/{n} attacks succeeded; Jeffreys-smoothed prevention rate.')
  self.add(p,'auto-mode','Auto Mode','Appendix C, Figure 13','Claude Opus 5','Claude Opus 4.8',.33,condition='Pooled model-swap ablation',metric='blocked_episode',sd=.7,notes='67% mean attack success printed in Figure 13; the already represented outer bars are not duplicated.')
  for id,label,loc,notes in [
   ('auto-framing-escaping','Rendering: framing and escaping','Figures 5 and 9','Injection-rendering mitigation and full attacker–monitor grid.'),
   ('auto-monitor-tool-results','Monitor tool results','Section 4.7','Expanded context for multi-context attacks.'),
   ('auto-compaction-monitor','Compaction monitoring','Section 4.7','Compaction-review mitigation is part of hardened Auto Mode.'),
   ('auto-prior-block-context','Monitor shown prior blocks','Appendix A.3','Repeated-attempt ablation; retained as a distinct design variant.'),
   ('auto-affordances','Technique knowledge × monitor knowledge','Appendix B.2, Figure 12','Attacker-affordance grid, not a new defender algorithm.'),
   ('auto-visible-monitor','Monitor hidden versus visible','Appendix F, Figure 17','Attacker-knowledge ablation across simulated briefs.')]:self.qualitative(p,id,label,loc,notes,kind='ablation')
 def expand_shade(self):
  p='2511.02997';self.drop(p,'Replaced by all main protocol variants and full adaptive-response tables.')
  # Values printed in Figures 1,2,4 are added by the figure transcription pass.
  for table,prot,label in [('S4.T1','shade-resample-then-defer-20','Resample then defer (threshold 20)'),('S5.T2','shade-critical-20','Defer on critical (threshold 20)')]:
   for row in self.rows(p,table)[1:]:
    if len(row)!=3 or not re.search(r'\d',row[1]):continue
    s=row[1];kwargs={}
    if '–' in s:
     a,b=map(float,s.split('–'));kwargs=dict(lower=a,upper=min(.9999,b))
    else:kwargs=dict(value=float(s))
    self.add(p,prot,label,'Table '+('1' if table=='S4.T1' else '2'),'Claude 3.7 Sonnet','Claude 3.5 Sonnet (new)',condition=row[0],context='red strategy:'+row[0],sd=.65,notes='The table also reports attack-policy main-task performance; it is not assumed to be a benign-usefulness budget.',**kwargs)
  self.add(p,'shade-pure-resample-full-context','Pure resample with full context','Section 3.2','Claude 3.7 Sonnet','Claude 3.5 Sonnet (new)',.87,usefulness=.93)
  for id,label in [('pure-resample','Pure resample'),('defer-trusted','Defer to trusted'),('defer-resample','Defer to resample'),('resample-then-defer','Resample then defer'),('critical','Defer on critical'),('notes','Defer to trusted with notes'),('permanent-notepad','Independent choice: permanent notepad'),('resample-only','Independent choice: resample only'),('defer-only','Independent choice: defer only'),('ephemeral-notepad','Independent choice: ephemeral notepad'),('resample-or-defer','Independent choice: resample or defer'),('interrogate','Independent choice: interrogate')]:
   self.qualitative(p,'shade-'+id,label,'Figures 1,2,4,5','Main and monitor-affordance variants; exact figure extraction tracked in the coverage ledger.')
 def expand_linux(self):
  p='2604.15384';self.drop(p,'Replaced by complete 11-monitor Figure 10 and attack/ablation coverage.')
  mons=['Claude Opus 4.6','Claude Sonnet 4.6','Gemini 3.1 Pro','GLM-5','GPT-5.4','Gemini 3 Flash','Claude Haiku 4.5','Kimi K2.5','GPT-5 mini','gpt-oss-120b','GPT-5 Nano']
  plain=[99,97,95,98,91,89,97,94,90,92,65];strategies=[98,90,100,98,91,89,82,98,90,89,50]
  for m,a,b in zip(mons,plain,strategies):
   for condition,value in [('Base attacker',a),('Attacker + strategies',b)]:self.add(p,'linux-live-monitoring','LinuxArena live monitoring','Figure 10','Claude Opus 4.6',m,value/100,condition=condition,context=condition,fpr=.01,notes='Rounded safety labels printed in the 11-monitor figure.')
  for att,h in [('Claude Opus 4.6',.34),('Claude Sonnet 4.6',.40),('Gemini 3.1 Pro',.40),('GLM-5',.28),('Claude Haiku 4.5',.09),('Kimi K2.5',.08),('Gemini 3 Flash',.03),('Grok 4.1',.10)]:
   self.add(p,'linux-live-monitoring','LinuxArena live monitoring','Figure 7',att,'GPT-5 Nano',upper=1-h,condition='Base attacker',context='Base attacker',notes='Unsuccessful sabotage gives a safety upper bound, not measured detection.')
  for id,label,loc,notes in [
   ('human-attacks','Human-crafted LaStraj attacks','Figures 11,12,35','Human-versus-model attack comparison for every available monitor.'),
   ('obvious-attacks','Obvious versus subtle attack','Appendix C, Figure 17','Haiku attack-policy ablation.'),
   ('delayed','Delayed full-trajectory monitoring','Appendix C, Figure 18','Compared with live-only and live-or-delayed; delayed detection may occur after harm.'),
   ('combined','Live-or-delayed monitoring','Appendix C, Figure 18','Combined intervention rule.'),
   ('attacker-goals','Side-task information: goal / pseudocode / full scorer','Appendix C, Figure 19','Attack-information ablation.'),
   ('monitor-goals','Monitor with versus without side-task goals','Appendix C, Figure 20','Monitor-context ablation.'),
   ('ensemble','Delayed-monitor ensemble size','Appendix C, Figure 21','Ensemble-size sweep at 1% trajectory FPR.'),
   ('sandbox','Base / no network / no network and no service access','Figure 6 and Figure 29','Sandboxing changes safety and usefulness; all three conditions retained.'),
   ('scratchpad','Attacker with versus without scratchpad','Appendix D, Figure 30','Attacker-reasoning ablation.'),
   ('test-tool','Side-task test tool enabled versus disabled','Appendix I.1, Figure 31','Attack-verification-tool ablation.'),
   ('thinking','Attacker thinking: off / 1k / 4k / 16k / 64k','Appendix I.2, Figure 32','Attack-budget sweep.'),
   ('description','Attacker with versus without environment description','Appendix I.3, Figure 33','Task-context ablation.'),
   ('calibration','Matched-attacker versus shared-Opus calibration','Appendix I.4, Figure 34','False-positive calibration ablation.')]:self.qualitative(p,'linux-'+id,label,loc,notes,kind='ablation')
 def expand_selection(self):
  p='2606.06529';self.drop(p,'Full Table 2 replaces two headline points and corrects trusted-monitor identity.')
  settings=['BashArena','LinuxArena'];vals={('Start','BashArena'):[(.20,0,15),(.30,0,3),(.41,0,3)],('Start','LinuxArena'):[(.31,.11,18),(.56,.35,20),(.77,.67,61)],('Stop','BashArena'):[(.20,0,2),(.30,.13,15),(.42,.37,223)],('Stop','LinuxArena'):[(.36,.09,23),(.61,.47,17),(.79,.79,28)]}
  for (policy,setting),rows in vals.items():
   for audit,(base,filtered,n) in zip([.01,.02,.05],rows):
    for condition,s in [('Baseline',base),(policy+' selection',filtered)]:
     self.add(p,'selection-'+slug(setting),'Trusted monitoring ('+setting+')','Table 2','Claude Opus 4.6','MiMo-V2-Flash',s,condition=f'{condition}, {audit:.0%} auditing',context=setting+' '+condition,fpr=audit,sd=1.5 if n<=3 else .9,notes=f'Held-out selected n={n}. Monitor is MiMo-V2-Flash; GPT-OSS is an offline selector, not the trusted monitor.')
  for id,label,loc,notes in [('joint','Combined start + stop','Section 4.3','Reported combined policy; LinuxArena effect is underpowered, with one trajectory surviving.'),('random','Random start and stop controls','Appendix E','Selection-rate controls.'),('last-step','Last-step stop policy','Appendix D.1','Stop-position ablation.'),('side-task','Best-side-task start policy','Appendix B.1','Side-task-choice ablation.')]:self.qualitative(p,'selection-'+id,label,loc,notes,kind='attack-policy ablation')
 def expand_bootstrap(self):
  p='2606.11998'
  # Replace worst-of-three summaries with the underlying three prompt results.
  self.obs[:]=[o for o in self.obs if not(o['study']==p and o['id'].endswith('-colluding'))]
  for row in self.rows(p,'A1.T4')[1:]:
   if len(row)!=7:continue
   raw,att,mon,*scores=row
   for name,cell in zip(['Default','Needle','Codewords'],scores[:3]):
    prot='bootstrapped-summary' if raw=='GPT-5.4' else 'bootstrapped-monitoring'
    label='Bootstrapping: summarized reasoning' if prot=='bootstrapped-summary' else 'Bootstrapped monitoring'
    self.add(p,prot,label,'Table 4',att,mon,num(cell)/100,condition=name+' collusion condition',metric='recall',context='collusion-'+name,sd=.7,notes='Underlying prompt-specific result replaces its redundant worst-of-three summary. Summary-routing architecture follows the documented Table 3 setup; helper identity is not a model feature.')
  for row in self.rows(p,'A4.T9')[2:]:
   if len(row)!=9:continue
   raw,att,mon,*scores=row
   for k,label in enumerate(['Reasoning only','Reasoning + actions','Reasoning + actions + stateful']):
    for j,condition in enumerate(['Honest','Default-colluding']):
     if k==2:continue # main honest and Default-colluding cells already in Tables 3 and 4
     prot=['bootstrapped-reasoning-only','bootstrapped-with-actions','bootstrapped-monitoring'][k]
     self.add(p,prot,'Bootstrapping: '+label,'Table 9',att,mon,num(scores[2*k+j])/100,condition=condition,metric='recall',context='ablation-'+condition,sd=.7)
  run=''
  for row in self.rows(p,'A3.T8')[2:]:
   if row[0].startswith('Run'):run=row[0];continue
   if len(row)==6 and row[0].isdigit():
    phase=row[0];self.add(p,'bootstrapped-refined-prompt','Bootstrapping: refined trusted prompt','Table 8','GPT-5.4','GPT-4.1 mini',num(row[3])/100,condition=run+' phase '+phase,metric='recall',fpr=num(row[4])/100,sd=1.,notes='Blue-winner catch after red-blue alternation; not a helper-capability feature.')
  self.qualitative(p,'bootstrapped-summary','Bootstrapping: summarized reasoning','Section 4.2, Figure 4','Reasoning-summary ablation; no helper identity or capability is modeled.',kind='ablation')
  self.qualitative(p,'bootstrapped-rollout-length','Rollout-length ablation','Section 4.3, Figure 5','Length-stratified catch and false-positive diagnostics.',kind='stratified analysis')
 def expand_monitoringbench(self):
  p='2605.09684'
  for row in self.rows(p,'A6.T6')[3:]:
   if len(row)!=17:continue
   mon=row[0];vals=[num(c)/100 for c in row[1:]]
   for k,stage in enumerate(['Baseline','Human strategies','Recon','Refined']):self.add(p,'monitoringbench-stepwise','Stepwise trusted monitoring','Table 6','Claude Opus 4.6',mon,sum(vals[4*k:4*k+4])/4,condition=stage,metric='recall',fpr=.01,context=stage,sd=.7,notes='Equal task-weighted mean of four published catch rates, matching the existing macro-average treatment.')
  for row in self.rows(p,'A3.T4')[2:6]:
   if len(row)!=7:continue
   condition=row[0]
   for mon,cell in zip(['GPT-5','GPT-5.1 Codex','Claude Opus 4.5','Claude Sonnet 4.5','Claude Sonnet 4'],row[2:]):
    rate=re.findall(r'(\d+(?:\.\d+)?)%',cell)
    if rate:self.add(p,'static-full-trajectory','Full-trajectory trusted monitoring','Table 4','Claude Opus 4.6',mon,float(rate[-1])/100,condition=condition+' cover opportunity',metric='recall',context='cover-'+condition,sd=.8)
  for row in self.rows(p,'A15.T16')[1:]:
   prompt,label,mon,scale,fpr,thr,caught,rate=row
   self.add(p,'monitoringbench-prompt-'+prompt,'Monitor prompt: '+label,'Table 16','Claude Opus 4.6',mon,num(rate)/100,condition='Prompt '+prompt+', FPR '+fpr,metric='recall',fpr=num(fpr)/100,context='prompt-sensitivity',sd=.8,notes='148-trajectory refined-attack subset; prompt/calibration variant.')
 def expand_untrusted(self):
  p='2602.20628';self.drop(p,'Replaced by complete signal-jamming/attack-strategy Table 2.')
  for row in self.rows(p,'S5.T2')[2:]:
   strategy,jam,*scores=row
   for dataset,idx in [('APPS',1),('BigCodeBench',3)]:
    cell=scores[idx]
    if cell=='-':continue
    value=num(cell)/100
    kwargs=dict(lower=.999) if '>' in cell else dict(value=value)
    self.add(p,'self-recognition-'+slug(jam),'Monitoring with '+jam,'Table 2','GPT-4.1','GPT-4o mini',condition=dataset+': '+strategy,context=dataset+' '+strategy,sd=.7,notes='Combined-monitor column; no separate untrusted-monitor capability is used.',**kwargs)
   # Untrusted-only columns are baselines, not trusted-chain candidates.
   for dataset,idx in [('APPS',0),('BigCodeBench',2)]:
    cell=scores[idx]
    if cell=='-':continue
    kwargs=dict(lower=.999) if '>' in cell else dict(value=num(cell)/100)
    self.add(p,'self-recognition-'+slug(jam)+'-without-trusted-review','Monitoring without trusted review: '+jam,'Table 2','GPT-4.1','GPT-4o mini',condition=dataset+': '+strategy,context=dataset+' '+strategy,sd=1.,kind='baseline',eligible=False,notes='No trusted review in this column; retained as baseline evidence, not a trusted-control candidate.',**kwargs)
 def expand_evasion(self):
  p='2609.30217';self.drop(p,'Single-run per-agent and monitor-ablation results replace the loose aggregate best-of-three bound.')
  agents=['GLM 5.2','DeepSeek V4 Flash','Muse Spark 1.3','GPT-5.6 Luna','GLM 5.3 Flash','GPT-5.6 Sol','GPT-6 Sol','Claude Fable 5.1','Claude Opus 5','GPT-6 Astra'];h=[.70,.33,.40,.35,.32,.16,.16,.06,.02,0]
  for a,success in zip(agents,h):self.add(p,'evasion-native-hooks','Native-hook trusted monitoring','Figure 1',a,'gpt-oss-120b',upper=1-success,condition='Single run',metric='blocked_episode',sd=1.,notes='One minus single-run evasion is a prevention upper bound; refusals are not credited as monitor catches.')
  for mon,success in [('gpt-oss-120b',.176),('Llama 3.1 8B',.353),('Qwen 3.6 35B-A3B',.412),('Qwen 3.5 9B',.147),('Qwen 3.5 35B-A3B',.5)]:self.add(p,'evasion-native-hooks','Native-hook trusted monitoring','Figure 8a','GPT-5.6 Sol',mon,upper=1-success,condition='34-task monitor sweep',metric='blocked_episode',sd=1.,context='34-task-sweep')
  for a,generic,reason in [('GPT-5.6 Luna',.475,.55),('DeepSeek V4 Flash',.35,.625)]:
   for name,h3 in [('Generic denial',generic),('Denial with reason',reason)]:self.add(p,'evasion-'+slug(name),name,'Figure 9',a,'gpt-oss-120b',upper=1-h3/3,condition='Best of three',metric='blocked_episode',sd=1.2,notes='Union-bound conversion H3/3; attempts are not assumed independent.')
  for a,aware,myopic in [('DeepSeek V4 Flash',.275,.85),('Muse Spark 1.3',.375,.675),('GPT-5.6 Luna',.325,.60),('GPT-5.6 Sol',.125,.175),('Claude Sonnet 5',.051,.065),('Claude Opus 5',.025,.077)]:
   for name,h in [('History-aware monitor',aware),('Myopic monitor',myopic)]:self.add(p,'evasion-'+slug(name),name,'Figure 10',a,'gpt-oss-120b',upper=1-h,condition='40-task subset',metric='blocked_episode',sd=1.2,notes='Refusal/downgrade caveats retained for Sonnet and Opus.')
  for id,label,loc,notes in [('effort','Reasoning effort: low / medium / high / xhigh / max','Figure 3','Four agent families across five effort levels; full curve indexed, not assigned fabricated scalar outcomes.'),('forged-denial','Forged-denial / denial-of-service diagnostics','Figure 7 and Table 9','Task abandonment and compliance diagnostic, not harmful-side-task prevention.'),('context-routes','Monitor context and interception routes','Tables 7–8, Appendix G','Control and interception diagnostics.')]:self.qualitative(p,'evasion-'+id,label,loc,notes,kind='ablation')
 def expand_remaining(self):
  p='2605.26047'
  self.drop(p,'Replaced headline resampling summaries with operating-point and aggregation variants.')
  for id,label,val in [('trusted-monitoring','Trusted monitoring',.61),('feedback','Retry with feedback',.60),('resample-min-2','Policy resample: minimum of 2',.48),('resample-max-2','Policy resample: maximum of 2',.68),('resample-max-5','Policy resample: maximum of 5',.71),('execute-2','Execute then resample',.72)]:
   self.add(p,'retry-'+id,label,'Figure 1','Claude Opus 4.6','MiMo-V2-Flash',val,fpr=.003,sd=.7,notes='Reported main operating point; sampling changes compute cost.')
  for rule,vals in [('max',[.61,.678,.698,.709,.711]),('median',[.61,.504,.568,.515,.566]),('min',[.61,.478,.394,.343,.307])]:
   for n,val in enumerate(vals,1):
    if n==1 or (rule,n) in [('max',2),('max',5),('min',2)]:continue
    self.add(p,f'retry-resample-{rule}-{n}',f'Policy resample: {rule} of {n}','Figure 3','Claude Opus 4.6','MiMo-V2-Flash',lower=val-.015,upper=val+.015,sd=.8,cost=f'{n} policy samples',notes='Figure readout interval, not a statistical confidence interval.')
  for k,val in [(2,.436),(3,.242),(4,.137),(5,.075)]:self.add(p,f'retry-{k}-strikes',f'{k}-strikes retry','Figure 18','Claude Opus 4.6','MiMo-V2-Flash',lower=val-.015,upper=val+.015,sd=.8)
  for id,label,loc in [('monitor-aggregation','Monitor aggregation: max, mean, median, 75th and 90th percentiles; 1–10 samples','Figure 15'),('two-stage','Two-stage conditional resampling; second-stage sizes 1–4','Figure 6'),('incremental','Incremental resampling: flat and rising thresholds','Figure 6'),('feedback-iid','Feedback versus IID and adaptive attackers','Figure 2'),('selective-caution','Selective caution','Figure 2'),('inconsistent','Inconsistent-attacker resampling','Figure 8'),('audit-rules','Auditor context, audit-win rules and audit-budget sweep','Appendices'),('shuffled','Synthetic shuffled-correlation and order-statistic controls','Figures 4–5')]:self.qualitative(p,'retry-'+id,label,loc,'Indexed separately; curve family retained without assigning an unsupported common scalar.',kind='ablation')
  p='2510.09462'
  self.drop(p,'Replaced headline adaptive-attack summaries with full monitor-target matrix and named protocol variants.')
  for mon,vals in [('GPT-4',[.126,.325,.439,.504]),('GPT-4o',[.181,.211,.126,.644]),('GPT-4.1',[.119,.125,.124,.780])]:
   for attack,val in zip(['GPT-4 targeted injection','GPT-4o targeted injection','GPT-4.1 targeted injection','No injection'],vals):self.add(p,'adaptive-trusted-monitoring','Adaptive-attack trusted monitoring','Figure 4','GPT-5',mon,val,condition=attack,context=attack,sd=.7)
  for id,label,val in [('upfront','Upfront auditing',.15),('zero-shot-injection','Trusted monitoring: zero-shot injection',.19),('zero-shot-clean','Trusted monitoring: no injection',.33)]:self.add(p,'adaptive-'+id,label,'Figure 6','GPT-5','GPT-4o mini',val,sd=.8)
  for id,label in [('dtr','Defer to resample'),('dtt','Defer to trusted'),('editing','Trusted editing'),('editing-monitor-sweep','Trusted editing across GPT-4, GPT-4o and GPT-4.1'),('bashbench-dtr','BashBench defer to resample'),('bashbench-dtt','BashBench defer to trusted'),('min-max','Minimum versus maximum resample score'),('audit-budgets','Audit budgets 1%, 2%, 4%'),('harm-timing','Immediate versus end-of-trajectory harm detection')]:self.qualitative(p,'adaptive-'+id,label,'Figures 3,5,8,10–12','Published safety/usefulness curves and calibration variants; indexed without selecting an arbitrary shared operating point.',kind='ablation')
  for p in ['2504.18530','2512.22154']:
   source=self.source(p)
   self.qualitative(p,'theory-'+p,'Theoretical control constructions and parameter sweeps','Full paper','Analytical evidence informs structure; not treated as empirical safety measurements.',kind='theory')
  # Explicit figure operating points, with digitization intervals rather than false precision.
  p='2511.02997'
  for id,label,val,u in [('pure-resample','Pure resample',.73,.977),('defer-trusted','Defer to trusted',.77,.82),('defer-resample','Defer to resample',.83,.895),('resample-then-defer','Resample then defer',.89,1.01),('critical','Defer on critical',.91,.70)]:self.add(p,'shade-'+id,label,'Figure 1','Claude 3.7 Sonnet','Claude 3.5 Sonnet (new)',lower=val-.02,upper=val+.02,usefulness=u,sd=.8,notes='Approximate plotted operating point; readout interval is not a confidence interval. Resample-then-defer prose and figure differ; retained figure point has additional transport uncertainty.')
  for id,label,val,u in [('permanent-notepad','Independent choice: permanent notepad',.24,.87),('resample-only','Independent choice: resample only',.125,1.14),('defer-only','Independent choice: defer only',.155,.879),('ephemeral-notepad','Independent choice: ephemeral notepad',.83,.90),('resample-or-defer','Independent choice: resample or defer',.855,.895),('interrogate','Independent choice: interrogate',.233,.72)]:self.add(p,'shade-'+id,label,'Figure 4','Claude 3.7 Sonnet','Claude 3.5 Sonnet (new)',lower=val-.02,upper=val+.02,usefulness=u,sd=.8,notes='Approximate plotted operating point; digitization interval, not confidence interval.')
  for id,label in [('thresholds','Suspicion thresholds and safety/usefulness sweeps'),('resample-count','Resample count and selection-rule heatmaps')]:self.qualitative(p,'shade-'+id,label,'Figures 5,7–8','Entire parameter sweep indexed; no invented per-cell values.',kind='ablation')
 def expand_figure_points(self):
  note='Approximate published figure readout; the interval represents digitization, not a statistical confidence interval. Extra transport uncertainty retained.'
  p='2605.26047'
  agg={'max':[.483,.578,.609,.625,.637,.652,.668,.680,.691,.698],'p90':[.483,.575,.604,.602,.565,.580,.594,.615,.625,.636],'p75':[.483,.570,.524,.522,.543,.564,.555,.543,.556,.567],'median':[.483,.523,.463,.505,.457,.480,.447,.467,.444,.455],'mean':[.483,.523,.487,.511,.523,.516,.519,.522,.521,.521]}
  for rule,vals in agg.items():
   for n,v in enumerate(vals,1):
    if n==1 and rule!='max':continue
    self.add(p,f'retry-monitor-{rule}-{n}',f'Monitor sampling: {rule} of {n}','Figure 15','Claude Opus 4.6','MiMo-V2-Flash',lower=v-.02,upper=v+.02,sd=.9,context='monitor-aggregation',cost=f'{n} monitor samples',notes=note)
  for n,v in [(1,.664),(2,.704),(3,.708),(4,.713)]:self.add(p,f'retry-two-stage-{n}',f'Two-stage conditional resampling: second stage {n}','Figure 6','Claude Opus 4.6','MiMo-V2-Flash',lower=v-.02,upper=v+.02,sd=.9,context='conditional-resampling',cost=f'Worst-case policy calls approximately {n+1}',notes=note)
  for rule,v in [('rising',.707),('flat',.713)]:self.add(p,'retry-incremental-'+rule,'Incremental resampling: '+rule,'Figure 6','Claude Opus 4.6','MiMo-V2-Flash',lower=v-.02,upper=v+.02,sd=.9,context='conditional-resampling',notes=note)
  p='2510.09462'
  for id,label,lo,hi in [('dtr','Defer to resample',.50,.60),('dtt','Defer to trusted',.55,.65),('editing','Trusted editing',.55,.65)]:
   for attack,a,b in [('ordinary',lo,hi),('injected',.10 if id=='dtr' else .15,.16 if id=='dtr' else .25)]:self.add(p,'adaptive-'+id,label,'Figure 3','GPT-5','GPT-4',lower=a,upper=b,condition=attack,usefulness=.94,sd=1.,context='APPS-'+attack,notes=note+' Read at approximately 94% usefulness.')
  for id,label,lo,hi in [('bashbench-dtr','BashBench defer to resample',.65,.75),('bashbench-dtt','BashBench defer to trusted',.68,.78)]:
   for attack,a,b in [('ordinary',lo,hi),('injected',.14 if id.endswith('dtr') else .18,.23 if id.endswith('dtr') else .28)]:self.add(p,'adaptive-'+id,label,'Figure 5','Claude Sonnet 4','GPT-4o',lower=a,upper=b,condition=attack,usefulness=.74,sd=1.1,context='BashBench-'+attack,notes=note+' Read at approximately 74% usefulness.')
  p='2604.15384'
  for id,label,v in [('delayed','Delayed full-trajectory monitoring',.43),('combined','Live-or-delayed monitoring',.84)]:self.add(p,'linux-'+id,label,'Figure 18','Claude Haiku 4.5','GPT-5 Nano',lower=v-.03,upper=v+.03,sd=1.,fpr=.01,context='timing',notes=note+' Delayed detection may occur after harm.')
  for n,v in [(1,.17),(2,.35),(4,.45),(8,.50),(16,.52),(32,.53)]:self.add(p,'linux-delayed-ensemble-'+str(n),f'Delayed-monitor ensemble: {n} samples','Figure 21','Claude Haiku 4.5','GPT-5 Nano',lower=v-.015,upper=v+.015,sd=1.,fpr=.01,context='ensemble',notes=note+' Extrapolated 64/128-sample points are indexed rather than treated as measured.')
  for id,label,v in [('no-network','No-network sandbox',.93),('editor-only','No-network, editor-only sandbox',.95)]:self.add(p,'linux-sandbox-'+id,label,'Figure 29','Claude Haiku 4.5','GPT-5 Nano',lower=v-.03,upper=min(.999,v+.03),sd=1.2,fpr=.01,context='sandbox',cost='Sandbox restrictions change usefulness; no matched cost normalization available.',notes=note)
  self.add(p,'linux-no-scratchpad','Attacker without scratchpad','Figure 30','Claude Opus 4.6','GPT-5 Nano',lower=.75,upper=.81,sd=1.,fpr=.01,context='scratchpad',notes=note)
  for budget,v in [('off',.93),('1k',.67),('4k',.92),('16k',.89),('64k',.875)]:self.add(p,'linux-thinking-'+budget,'Attacker thinking: '+budget,'Figure 32','Claude Opus 4.6','GPT-5 Nano',lower=v-.04,upper=v+.04,sd=1.1,fpr=.01,context='thinking',notes=note+' Attacker-compute ablation; no independent model capability improvement inferred.')
  mons=['GPT-4.1 Nano','GPT-5 Nano','gpt-oss-120b','Claude Haiku 4.5','GPT-5 mini','Claude Sonnet 4.6','GPT-5.4','Kimi K2.5','Gemini 3 Flash','GLM-5','Gemini 3.1 Pro','Claude Opus 4.6']
  human=[97,94,69,50,49,49,45,45,39,27,21,13];model=[54,47,17,5,7,2,5,3,10,2,0,1]
  for mon,h,m in zip(mons,human,model):
   for context,v in [('Human-crafted',h),('Matched Opus attacks',m)]:
    self.add(p,'linux-conditional-catch','Conditional catch of successful side-task attacks','Figure 35','Claude Opus 4.6',mon,1-v/100,condition=context,metric='recall',sd=1.5 if context=='Human-crafted' else 1.,context='conditional-'+context,fpr=.01,notes='Rounded evasion labels converted to conditional catch, not deployment safety. Human attacks have no assigned METR horizon.')
    if context=='Human-crafted':self.obs[-1]['extra_attack']='human-crafted'
  # Preserve the summary-versus-raw architectural distinction without a helper feature.
  for o in self.obs:
   if o['study']=='2606.11998' and 'Only summarized helper reasoning' in o.get('detail',''):o['protocol_variant']='bootstrapped-summary'
 def expand_conceptual(self):
  for id,label in [('synchronous','Fully synchronous monitoring'),('semi-synchronous','Semi-synchronous monitoring'),('asynchronous','Asynchronous monitoring')]:self.qualitative('2512.22154','practical-'+id,label,'Monitoring taxonomy and case studies','Conceptual latency, parallelism and recovery analysis; no fabricated historical safety datapoint.',kind='conceptual protocol')
  for id,label in [('mafia','Mafia auditing'),('backdoor-code','Backdoor-code auditing'),('debate','Adversarial debate'),('wargames','Wargame containment'),('nested','Nested scalable oversight')]:self.qualitative('2504.18530','scaling-'+id,label,'Game-specific scaling and nested oversight analysis','Domain-specific game outcomes and analytical scaling constraints do not directly measure deployment control safety.',kind='structural evidence')
 def finish(self):
  # Register existing rows as well, preserving selected evidence from other papers.
  for o in self.obs:
   pid=o['study'];id=o.get('protocol_variant',o['protocol'])
   if pid=='2606.11998':
    if id.startswith('bootstrap-') and id not in ['bootstrap-trusted-only','bootstrap-helper-only','bootstrap-direct-monitor']:id='bootstrapped-monitoring'
    if id=='bootstrap-helper-only':id='bootstrap-direct-monitor'
   label=o.get('protocol_label',{'bootstrapped-monitoring':'Bootstrapped monitoring','bootstrap-direct-monitor':'Direct monitoring (bootstrapping study)'}.get(id,id))
   v=self.register(pid,id,label,o.get('source_location','Original ledger'),notes='')
   if o['id'] not in v['observation_ids']:v['observation_ids'].append(o['id'])
  attack_only={'linux-no-scratchpad','adaptive-zero-shot-injection','adaptive-zero-shot-clean'}
  for o in self.obs:
   if o['protocol'].startswith('linux-thinking-') or o['protocol'] in attack_only:o['leader_eligible']=False
  for v in self.variants.values():
   if v['id'].startswith('linux-thinking-') or v['id'] in attack_only:
    v['leader_eligible']=False;v['notes']+=' Attacker-context ablation: numerical evidence retained, not a distinct defender candidate.'
  for v in self.variants.values():v['status']='quantitative' if v['observation_ids'] else 'indexed; no scalar extracted'
  self.data['variants']=list(self.variants.values());self.data['observations']=self.obs
  self.data['variant_scope']='Distinct control mechanisms, named ablations and material operating-point variants found in all linked papers. Figure-only and conceptual variants are indexed explicitly, not fabricated into numerical results.'
  (ROOT/'evidence.json').write_text(json.dumps(self.data,indent=2)+'\n')
  (ROOT/'variant_inventory.json').write_text(json.dumps(self.data['variants'],indent=2)+'\n')
  print(len(self.obs),'observations;',len(self.variants),'indexed variants;',sum(v['status']=='quantitative' for v in self.variants.values()),'with quantitative evidence')

def expand_main():
 a=argparse.ArgumentParser();a.add_argument('--cache',default='/tmp/control-variant-sources');args=a.parse_args();e=Expansion(args.cache)
 for method in ['expand_greenblatt','expand_ctrlz','expand_auto','expand_shade','expand_linux','expand_selection','expand_bootstrap','expand_monitoringbench','expand_untrusted','expand_evasion','expand_remaining','expand_figure_points','expand_conceptual']:getattr(e,method)()
 e.finish()


# Source refresh
def fetch_source(pid, root):
 import requests
 from bs4 import BeautifulSoup
 url='https://arxiv.org/html/'+pid;r=requests.get(url,timeout=90);r.raise_for_status();(root/(pid+'.html')).write_text(r.text);s=BeautifulSoup(r.text,'html.parser');tables=[];figures=[]
 for el in s.select('figure'):
  c=el.find('figcaption');caption=c.get_text(' ',strip=True) if c else ''
  if el.select('table'):
   rows=[]
   for row in el.select('tr'):
    cells=[{'text':cell.get_text(' ',strip=True),'rowspan':cell.get('rowspan',1),'colspan':cell.get('colspan',1)} for cell in row.find_all(['th','td'],recursive=False)]
    if cells:rows.append(cells)
   tables.append(dict(id=el.get('id'),caption=caption,rows=rows))
  else:figures.append(dict(id=el.get('id'),caption=caption,images=[dict(src=i.get('src'),alt=i.get('alt')) for i in el.select('img')]))
 out=dict(url=url,tables=tables,figures=figures);(root/(pid+'.json')).write_text(json.dumps(out,indent=2));return pid,[(t['id'],t['caption'][:160],len(t['rows'])) for t in tables],[(f['id'],f['caption'][:120]) for f in figures[:8]]

def refresh_main():
 parser=argparse.ArgumentParser(description='Refresh primary-paper HTML and tables.')
 parser.add_argument('--cache',default='/tmp/control-variant-sources');args=parser.parse_args()
 root=Path(args.cache);root.mkdir(parents=True,exist_ok=True)
 ids=['2312.06942','2504.10374','2510.09462','2511.02997','2604.15384','2605.26047','2606.06529','2606.11998','2609.19587v2','2605.09684','2609.30217','2602.20628','2504.18530','2512.22154']
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for result in pool.map(lambda pid: fetch_source(pid, root), ids):print(json.dumps(result))


# Independent inference and coverage checks
from scipy.stats import truncnorm

class InferenceChecks(unittest.TestCase):
    def test_helper_identity_has_no_effect_on_fit_or_candidates(self):
        data = json.loads((ROOT / "evidence.json").read_text())
        changed = copy.deepcopy(data)
        for o in changed["observations"]:
            if o["study"] == "2606.11998" and o["protocol"] not in {"bootstrap-trusted-only", "bootstrap-helper-only"}:
                o["protocol"] = "bootstrap-an-arbitrary-other-helper"
                o["condition_effect"] = "arbitrary-helper-condition"
                o["evaluation_group"] = "arbitrary-helper-group"
                o["helper_capability"] = 10**12
        original_design = build_design(data, 1.5, 1.)
        changed_design = build_design(changed, 1.5, 1.)
        for first, second in zip(original_design, changed_design):
            np.testing.assert_equal(first, second)
        self.assertEqual(protocol_candidates(data), protocol_candidates(changed))
        projected = model_observations(data)
        self.assertEqual(len(projected), len(data["observations"]))
        bootstrap = [o for o in projected if o["study"] == "2606.11998"]
        self.assertTrue({"bootstrapped-monitoring", "bootstrap-trusted-only", "bootstrap-direct-monitor"}.issubset({o["protocol"] for o in bootstrap}))
        self.assertFalse(any("glm" in o["protocol"] or "gpt-5" in o["protocol"] for o in bootstrap))
        self.assertFalse(any("condition_effect" in o for o in bootstrap))

    def test_variant_coverage_and_candidate_roles(self):
        data = json.loads((ROOT / "evidence.json").read_text())
        validate_evidence(data)
        variants = {v["id"]: v for v in data["variants"]}
        for key in ["auto-mode-strict", "guardian-strict", "ctrlz-resample-time-travel-combined", "bootstrapped-with-actions"]:
            self.assertIn(key, variants)
            self.assertTrue(variants[key]["observation_ids"])
        self.assertEqual({v["study"] for v in variants.values()}, {o["study"] for o in data["observations"]} | {"2504.18530", "2512.22154"})
        selected = [o for o in data["observations"] if o["study"] == "2606.06529"]
        self.assertTrue(all(o["monitor"] == "MiMo-V2-Flash" for o in selected))
        candidates = {p["id"] for p in protocol_candidates(data)}
        self.assertTrue(all(o["protocol"] not in candidates for o in data["observations"] if not o.get("candidate_eligible", True) or not o.get("leader_eligible", True)))

    def test_truncation_in_both_extreme_tails(self):
        rng = np.random.default_rng(17)
        for lower, upper in [(12., np.inf), (-np.inf, -12.), (-1., 2.)]:
            sample = truncated_normal(rng, np.zeros(50000), 1., lower, upper)
            scalar = np.array([truncated_scalar(rng, 0., 1., lower, upper) for _ in range(10000)])
            expected, variance = truncnorm.stats(lower, upper, moments="mv")
            self.assertLess(abs(scalar.mean() - expected), 5 * np.sqrt(variance / len(scalar)))
            self.assertTrue(np.all(sample >= lower))
            self.assertTrue(np.all(sample <= upper))
            self.assertLess(abs(sample.mean() - expected), 5 * np.sqrt(variance / len(sample)))

    def test_collapsed_gibbs_against_direct_gaussian_rejection(self):
        data = {"observations": [
            dict(id=str(i), year=t, ln_monitor=m, ln_attacker=a, study="one",
                 protocol="one", metric="safety", value=float(expit(y)), logit_sd=.7)
            for i, (t, m, a, y) in enumerate([
                (0., 0., 0., .2), (.5, 1., .2, .9), (1., .2, 1., -.2),
                (1.5, .5, .4, .8), (2., 1., .8, .7)])]}
        x, y, noise, _, _, _, _, means, sds, positive = build_design(data, .75, 1.)
        xc, xu = x[:, positive], x[:, ~positive]
        covariance = np.diag(noise**2) + (xu * sds[~positive]**2) @ xu.T
        inv = np.linalg.inv(covariance)
        q = xc.T @ inv @ xc + np.diag(1 / sds[positive]**2)
        cov = np.linalg.inv(q)
        mean = cov @ (xc.T @ inv @ y + means[positive] / sds[positive]**2)
        direct = np.random.default_rng(31).multivariate_normal(mean, cov, size=500000)
        direct = direct[(direct >= 0).all(axis=1)]
        self.assertGreater(len(direct), 3000)
        chains, _, _ = sample(data, .75, 1., 2500, 1500, 4)
        sampled = chains[:, :, 1:].reshape(-1, direct.shape[1])
        # Independent truncated multivariate-normal rejection is the reference.
        self.assertTrue(np.all(abs(sampled.mean(axis=0) - direct.mean(axis=0)) < .08))
        self.assertLess(split_rhat(chains[:, :, :4]).max(), 1.03)

    def test_trend_sign_matches_horizon_growth(self):
        rng = np.random.default_rng(47)
        gp, bm, ba, gf, gm = rng.uniform(.01, 3, (5, 1000))
        control_growth = (gp + bm * gm) / ba
        self.assertTrue(np.array_equal(control_growth > gf, gp + bm * gm - ba * gf > 0))



def main():
    actions = {"fit": fit_main, "refresh": refresh_main, "expand": expand_main,
               "test": lambda: unittest.main(argv=[sys.argv[0], *sys.argv[1:]])}
    if len(sys.argv) > 1 and sys.argv[1] in actions:
        action = sys.argv.pop(1)
        actions[action]()
    elif len(sys.argv) > 1 and sys.argv[1] in {"-h", "--help"}:
        print("Usage: python ai_control.py {fit,refresh,expand,test} [options]\n"
              "  fit      Fit the model and regenerate chart data (default)\n"
              "  refresh  Download primary-paper HTML and tables\n"
              "  expand   Rebuild evidence and variant inventory from cached sources\n"
              "  test     Run numerical and evidence checks\n"
              "Use a command followed by --help for its options.")
    else:
        fit_main()


if __name__ == "__main__":
    main()
