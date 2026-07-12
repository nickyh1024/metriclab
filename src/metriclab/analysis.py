"""Statistical analysis for a two-arm randomized experiment."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import NormalDist

import pandas as pd


@dataclass(frozen=True)
class ExperimentResult:
    control_users: int
    treatment_users: int
    control_conversion: float
    treatment_conversion: float
    absolute_lift: float
    relative_lift: float
    confidence_interval: tuple[float, float]
    p_value: float
    control_revenue_per_user: float
    treatment_revenue_per_user: float
    recommendation: str


def analyze_experiment(data: pd.DataFrame, alpha: float = 0.05) -> ExperimentResult:
    """Analyze user-level binary conversion and revenue outcomes."""
    required = {"user_id", "variant", "purchased", "revenue"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    if data["user_id"].duplicated().any():
        raise ValueError("each user must appear exactly once")
    if set(data["variant"].unique()) != {"control", "treatment"}:
        raise ValueError("variant must contain control and treatment")
    if not data["purchased"].isin([0, 1]).all():
        raise ValueError("purchased must be binary")

    control = data.loc[data["variant"] == "control"]
    treatment = data.loc[data["variant"] == "treatment"]
    n_c, n_t = len(control), len(treatment)
    p_c = float(control["purchased"].mean())
    p_t = float(treatment["purchased"].mean())
    lift = p_t - p_c

    unpooled_se = sqrt(p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t)
    normal = NormalDist()
    critical = normal.inv_cdf(1 - alpha / 2)
    confidence_interval = (lift - critical * unpooled_se, lift + critical * unpooled_se)

    pooled = float(data["purchased"].mean())
    pooled_se = sqrt(pooled * (1 - pooled) * (1 / n_c + 1 / n_t))
    z_score = lift / pooled_se if pooled_se else 0.0
    p_value = float(2 * (1 - normal.cdf(abs(z_score))))

    control_rpu = float(control["revenue"].mean())
    treatment_rpu = float(treatment["revenue"].mean())
    if p_value < alpha and lift > 0 and treatment_rpu >= control_rpu * 0.98:
        recommendation = "Ship"
    elif p_value < alpha and lift < 0:
        recommendation = "Stop"
    else:
        recommendation = "Iterate"

    return ExperimentResult(
        control_users=n_c,
        treatment_users=n_t,
        control_conversion=p_c,
        treatment_conversion=p_t,
        absolute_lift=lift,
        relative_lift=lift / p_c if p_c else float("nan"),
        confidence_interval=confidence_interval,
        p_value=p_value,
        control_revenue_per_user=control_rpu,
        treatment_revenue_per_user=treatment_rpu,
        recommendation=recommendation,
    )
