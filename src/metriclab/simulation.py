"""Transparent synthetic data for developing the MetricLab workflow."""

from __future__ import annotations

import numpy as np
import pandas as pd


def simulate_checkout_experiment(
    n_users: int = 20_000,
    baseline_conversion: float = 0.12,
    absolute_treatment_effect: float = 0.012,
    seed: int = 42,
) -> pd.DataFrame:
    """Return user-level outcomes for a simulated randomized checkout test.

    Treatment assignment and outcomes are generated independently from a fixed
    seed. Revenue is zero for non-purchasers and log-normally distributed for
    purchasers. The treatment effect is injected and must not be interpreted as
    a real-world causal estimate.
    """
    if n_users < 2:
        raise ValueError("n_users must be at least 2")
    if not 0 < baseline_conversion < 1:
        raise ValueError("baseline_conversion must be between 0 and 1")
    treatment_conversion = baseline_conversion + absolute_treatment_effect
    if not 0 < treatment_conversion < 1:
        raise ValueError("treatment conversion must be between 0 and 1")

    rng = np.random.default_rng(seed)
    user_ids = np.arange(1, n_users + 1)
    treatment = rng.binomial(1, 0.5, size=n_users)
    probability = baseline_conversion + treatment * absolute_treatment_effect
    purchased = rng.binomial(1, probability)
    order_value = rng.lognormal(mean=4.3, sigma=0.45, size=n_users)
    revenue = purchased * order_value

    return pd.DataFrame(
        {
            "user_id": user_ids,
            "variant": np.where(treatment == 1, "treatment", "control"),
            "purchased": purchased,
            "revenue": revenue,
        }
    )

