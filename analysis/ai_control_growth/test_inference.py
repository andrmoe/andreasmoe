"""Numerical checks of the actual inference, not snapshots of fitted results."""

import unittest
import copy
import json

import numpy as np
from scipy.stats import truncnorm

import model


class InferenceChecks(unittest.TestCase):
    def test_helper_identity_has_no_effect_on_fit_or_candidates(self):
        data = json.loads((model.ROOT / "evidence.json").read_text())
        changed = copy.deepcopy(data)
        for o in changed["observations"]:
            if o["study"] == "2606.11998" and o["protocol"] not in {"bootstrap-trusted-only", "bootstrap-helper-only"}:
                o["protocol"] = "bootstrap-an-arbitrary-other-helper"
                o["condition_effect"] = "arbitrary-helper-condition"
                o["evaluation_group"] = "arbitrary-helper-group"
                o["helper_capability"] = 10**12
        original_design = model.build_design(data, 1.5, 1.)
        changed_design = model.build_design(changed, 1.5, 1.)
        for first, second in zip(original_design, changed_design):
            np.testing.assert_equal(first, second)
        self.assertEqual(model.protocol_candidates(data), model.protocol_candidates(changed))
        projected = model.model_observations(data)
        self.assertEqual(len(projected), len(data["observations"]))
        bootstrap = [o for o in projected if o["study"] == "2606.11998"]
        self.assertTrue({"bootstrapped-monitoring", "bootstrap-trusted-only", "bootstrap-direct-monitor"}.issubset({o["protocol"] for o in bootstrap}))
        self.assertFalse(any("glm" in o["protocol"] or "gpt-5" in o["protocol"] for o in bootstrap))
        self.assertFalse(any("condition_effect" in o for o in bootstrap))

    def test_variant_coverage_and_candidate_roles(self):
        data = json.loads((model.ROOT / "evidence.json").read_text())
        model.validate_evidence(data)
        variants = {v["id"]: v for v in data["variants"]}
        for key in ["auto-mode-strict", "guardian-strict", "ctrlz-resample-time-travel-combined", "bootstrapped-with-actions"]:
            self.assertIn(key, variants)
            self.assertTrue(variants[key]["observation_ids"])
        self.assertEqual({v["study"] for v in variants.values()}, {o["study"] for o in data["observations"]} | {"2504.18530", "2512.22154"})
        selected = [o for o in data["observations"] if o["study"] == "2606.06529"]
        self.assertTrue(all(o["monitor"] == "MiMo-V2-Flash" for o in selected))
        candidates = {p["id"] for p in model.protocol_candidates(data)}
        self.assertTrue(all(o["protocol"] not in candidates for o in data["observations"] if not o.get("candidate_eligible", True) or not o.get("leader_eligible", True)))

    def test_truncation_in_both_extreme_tails(self):
        rng = np.random.default_rng(17)
        for lower, upper in [(12., np.inf), (-np.inf, -12.), (-1., 2.)]:
            sample = model.truncated_normal(rng, np.zeros(50000), 1., lower, upper)
            scalar = np.array([model.truncated_scalar(rng, 0., 1., lower, upper) for _ in range(10000)])
            expected, variance = truncnorm.stats(lower, upper, moments="mv")
            self.assertLess(abs(scalar.mean() - expected), 5 * np.sqrt(variance / len(scalar)))
            self.assertTrue(np.all(sample >= lower))
            self.assertTrue(np.all(sample <= upper))
            self.assertLess(abs(sample.mean() - expected), 5 * np.sqrt(variance / len(sample)))

    def test_collapsed_gibbs_against_direct_gaussian_rejection(self):
        data = {"observations": [
            dict(id=str(i), year=t, ln_monitor=m, ln_attacker=a, study="one",
                 protocol="one", metric="safety", value=float(model.expit(y)), logit_sd=.7)
            for i, (t, m, a, y) in enumerate([
                (0., 0., 0., .2), (.5, 1., .2, .9), (1., .2, 1., -.2),
                (1.5, .5, .4, .8), (2., 1., .8, .7)])]}
        x, y, noise, _, _, _, _, means, sds, positive = model.build_design(data, .75, 1.)
        xc, xu = x[:, positive], x[:, ~positive]
        covariance = np.diag(noise**2) + (xu * sds[~positive]**2) @ xu.T
        inv = np.linalg.inv(covariance)
        q = xc.T @ inv @ xc + np.diag(1 / sds[positive]**2)
        cov = np.linalg.inv(q)
        mean = cov @ (xc.T @ inv @ y + means[positive] / sds[positive]**2)
        direct = np.random.default_rng(31).multivariate_normal(mean, cov, size=500000)
        direct = direct[(direct >= 0).all(axis=1)]
        self.assertGreater(len(direct), 3000)
        chains, _, _ = model.sample(data, .75, 1., 2500, 1500, 4)
        sampled = chains[:, :, 1:].reshape(-1, direct.shape[1])
        # Independent truncated multivariate-normal rejection is the reference.
        self.assertTrue(np.all(abs(sampled.mean(axis=0) - direct.mean(axis=0)) < .08))
        self.assertLess(model.split_rhat(chains[:, :, :4]).max(), 1.03)

    def test_trend_sign_matches_horizon_growth(self):
        rng = np.random.default_rng(47)
        gp, bm, ba, gf, gm = rng.uniform(.01, 3, (5, 1000))
        control_growth = (gp + bm * gm) / ba
        self.assertTrue(np.array_equal(control_growth > gf, gp + bm * gm - ba * gf > 0))


if __name__ == "__main__":
    unittest.main()
