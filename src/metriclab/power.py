"""Sample-size planning for two-arm conversion experiments."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, sqrt
from statistics import NormalDist


@dataclass(frozen=True)
class PowerPlan:
    baseline_rate: float
    target_rate: float
    absolute_lift: float
    relative_lift: float
    alpha: float
    power: float
    users_per_variant: int
    total_users: int


def two_proportion_sample_size(
    baseline_rate: float,
    absolute_lift: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> PowerPlan:
    """Estimate equal-sized variants for a two-sided two-proportion z-test.

    The calculation assumes independent observations, stable conversion rates,
    equal allocation, and one primary comparison. Operational experiments may
    require additional allowance for attrition or clustering.
    """
    target_rate = baseline_rate + absolute_lift
    if not 0 < baseline_rate < 1:
        raise ValueError("baseline_rate must be between 0 and 1")
    if absolute_lift <= 0:
        raise ValueError("absolute_lift must be positive")
    if not 0 < target_rate < 1:
        raise ValueError("target_rate must be between 0 and 1")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")
    if not 0 < power < 1:
        raise ValueError("power must be between 0 and 1")

    normal = NormalDist()
    z_alpha = normal.inv_cdf(1 - alpha / 2)
    z_power = normal.inv_cdf(power)
    pooled_rate = (baseline_rate + target_rate) / 2

    numerator = (
        z_alpha * sqrt(2 * pooled_rate * (1 - pooled_rate))
        + z_power
        * sqrt(
            baseline_rate * (1 - baseline_rate)
            + target_rate * (1 - target_rate)
        )
    ) ** 2
    users_per_variant = ceil(numerator / absolute_lift**2)

    return PowerPlan(
        baseline_rate=baseline_rate,
        target_rate=target_rate,
        absolute_lift=absolute_lift,
        relative_lift=absolute_lift / baseline_rate,
        alpha=alpha,
        power=power,
        users_per_variant=users_per_variant,
        total_users=users_per_variant * 2,
    )

