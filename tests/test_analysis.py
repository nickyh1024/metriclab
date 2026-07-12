import unittest

import pandas as pd

from metriclab.analysis import analyze_experiment
from metriclab.simulation import simulate_checkout_experiment


class MetricLabTests(unittest.TestCase):
    def test_simulation_is_reproducible(self):
        first = simulate_checkout_experiment(n_users=100, seed=7)
        second = simulate_checkout_experiment(n_users=100, seed=7)
        pd.testing.assert_frame_equal(first, second)

    def test_analysis_detects_large_positive_effect(self):
        data = simulate_checkout_experiment(
            n_users=100_000,
            baseline_conversion=0.10,
            absolute_treatment_effect=0.04,
            seed=8,
        )
        result = analyze_experiment(data)
        self.assertGreater(result.absolute_lift, 0)
        self.assertLess(result.p_value, 0.05)
        self.assertGreater(result.confidence_interval[0], 0)

    def test_analysis_rejects_duplicate_users(self):
        data = simulate_checkout_experiment(n_users=100, seed=9)
        data.loc[1, "user_id"] = data.loc[0, "user_id"]
        with self.assertRaisesRegex(ValueError, "exactly once"):
            analyze_experiment(data)

    def test_simulation_validates_conversion_probability(self):
        with self.assertRaisesRegex(ValueError, "treatment conversion"):
            simulate_checkout_experiment(
                baseline_conversion=0.99,
                absolute_treatment_effect=0.02,
            )


if __name__ == "__main__":
    unittest.main()
