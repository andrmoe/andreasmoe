"""Exploratory Bayesian synthesis of trusted AI-control growth.

Run: python model.py [--draws 5000] [--burn 5000] [--chains 4]
Dependencies: numpy, scipy, matplotlib. No network access at inference time.
All probabilities are conditional on the transport and frontier-gap priors.
"""

from __future__ import annotations

import argparse
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


def main():
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
    target = ROOT.parents[1] / "ai_control_growth_data.js"
    target.write_text("// Generated by analysis/ai_control_growth/model.py; do not edit by hand.\n" +
                      "window.AI_CONTROL_GROWTH = " + json.dumps(page, separators=(",", ":")) + ";\n")


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


if __name__ == "__main__":
    main()
