import unittest

import pandas as pd

from metriclab.analysis import analyze_experiment, check_assignment_balance
from metriclab.power import two_proportion_sample_size
from metriclab.simulation import simulate_product_page_experiment


class MetricLabTests(unittest.TestCase):
    def test_simulation_is_reproducible(self):
        first = simulate_product_page_experiment(n_users=100, seed=7)
        second = simulate_product_page_experiment(n_users=100, seed=7)
        pd.testing.assert_frame_equal(first, second)

    def test_analysis_detects_large_positive_effect(self):
        data = simulate_product_page_experiment(
            n_users=100_000,
            baseline_conversion=0.10,
            absolute_treatment_effect=0.04,
            seed=8,
        )
        result = analyze_experiment(data)
        self.assertGreater(result.absolute_lift, 0)
        self.assertLess(result.p_value, 0.05)
        self.assertGreater(result.confidence_interval[0], 0)
        self.assertLessEqual(
            result.revenue_confidence_interval[0],
            result.revenue_difference,
        )
        self.assertGreaterEqual(
            result.revenue_confidence_interval[1],
            result.revenue_difference,
        )

    def test_analysis_rejects_duplicate_users(self):
        data = simulate_product_page_experiment(n_users=100, seed=9)
        data.loc[1, "user_id"] = data.loc[0, "user_id"]
        with self.assertRaisesRegex(ValueError, "exactly once"):
            analyze_experiment(data)

    def test_simulation_validates_conversion_probability(self):
        with self.assertRaisesRegex(ValueError, "treatment conversion"):
            simulate_product_page_experiment(
                baseline_conversion=0.99,
                absolute_treatment_effect=0.02,
            )

    def test_power_plan_grows_for_smaller_effect(self):
        small_effect = two_proportion_sample_size(0.183, 0.01)
        large_effect = two_proportion_sample_size(0.183, 0.02)
        self.assertGreater(
            small_effect.users_per_variant,
            large_effect.users_per_variant,
        )
        self.assertEqual(small_effect.total_users, small_effect.users_per_variant * 2)

    def test_power_plan_rejects_invalid_inputs(self):
        with self.assertRaisesRegex(ValueError, "absolute_lift"):
            two_proportion_sample_size(0.183, 0)

    def test_assignment_balance_passes_normal_random_split(self):
        data = simulate_product_page_experiment(n_users=20_000, seed=42)
        result = check_assignment_balance(data)
        self.assertTrue(result.passed)
        self.assertGreaterEqual(result.p_value, 0.01)

    def test_assignment_balance_detects_large_mismatch(self):
        data = simulate_product_page_experiment(n_users=20_000, seed=42)
        data.loc[:13_999, "variant"] = "treatment"
        data.loc[14_000:, "variant"] = "control"
        result = check_assignment_balance(data)
        self.assertFalse(result.passed)
        self.assertLess(result.p_value, 0.01)


if __name__ == "__main__":
    unittest.main()
