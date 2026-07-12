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
    revenue_difference: float
    revenue_relative_change: float
    revenue_confidence_interval: tuple[float, float]
    revenue_p_value: float
    recommendation: str


@dataclass(frozen=True)
class AssignmentBalanceResult:
    control_users: int
    treatment_users: int
    expected_treatment_share: float
    observed_treatment_share: float
    p_value: float
    passed: bool


def check_assignment_balance(
    data: pd.DataFrame,
    expected_treatment_share: float = 0.5,
    alpha: float = 0.01,
) -> AssignmentBalanceResult:
    """Check whether observed allocation is consistent with the planned split.

    This binomial normal-approximation check is commonly called a sample-ratio-
    mismatch (SRM) check. A low p-value indicates that the allocation difference
    is too large to dismiss as ordinary random variation.
    """
    if "variant" not in data.columns:
        raise ValueError("missing required column: variant")
    variants = set(data["variant"].unique())
    if variants != {"control", "treatment"}:
        raise ValueError("variant must contain control and treatment")
    if not 0 < expected_treatment_share < 1:
        raise ValueError("expected_treatment_share must be between 0 and 1")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")

    counts = data["variant"].value_counts()
    control_users = int(counts["control"])
    treatment_users = int(counts["treatment"])
    total_users = control_users + treatment_users
    observed_share = treatment_users / total_users
    standard_error = sqrt(
        expected_treatment_share
        * (1 - expected_treatment_share)
        / total_users
    )
    z_score = (observed_share - expected_treatment_share) / standard_error
    normal = NormalDist()
    p_value = float(2 * (1 - normal.cdf(abs(z_score))))

    return AssignmentBalanceResult(
        control_users=control_users,
        treatment_users=treatment_users,
        expected_treatment_share=expected_treatment_share,
        observed_treatment_share=observed_share,
        p_value=p_value,
        passed=p_value >= alpha,
    )


def analyze_experiment(data: pd.DataFrame, alpha: float = 0.05) -> ExperimentResult:
    """Analyze user-level binary conversion and revenue outcomes."""
    required = {"user_id", "variant", "converted", "revenue"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    if data["user_id"].duplicated().any():
        raise ValueError("each user must appear exactly once")
    if set(data["variant"].unique()) != {"control", "treatment"}:
        raise ValueError("variant must contain control and treatment")
    if not data["converted"].isin([0, 1]).all():
        raise ValueError("converted must be binary")

    control = data.loc[data["variant"] == "control"]
    treatment = data.loc[data["variant"] == "treatment"]
    n_c, n_t = len(control), len(treatment)
    p_c = float(control["converted"].mean())
    p_t = float(treatment["converted"].mean())
    lift = p_t - p_c

    unpooled_se = sqrt(p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t)
    normal = NormalDist()
    critical = normal.inv_cdf(1 - alpha / 2)
    confidence_interval = (lift - critical * unpooled_se, lift + critical * unpooled_se)

    pooled = float(data["converted"].mean())
    pooled_se = sqrt(pooled * (1 - pooled) * (1 / n_c + 1 / n_t))
    z_score = lift / pooled_se if pooled_se else 0.0
    p_value = float(2 * (1 - normal.cdf(abs(z_score))))

    control_rpu = float(control["revenue"].mean())
    treatment_rpu = float(treatment["revenue"].mean())
    revenue_difference = treatment_rpu - control_rpu
    revenue_relative_change = (
        revenue_difference / control_rpu
        if control_rpu
        else float("nan")
    )
    revenue_se = sqrt(
        float(control["revenue"].var(ddof=1)) / n_c
        + float(treatment["revenue"].var(ddof=1)) / n_t
    )
    revenue_ci = (
        revenue_difference - critical * revenue_se,
        revenue_difference + critical * revenue_se,
    )
    revenue_z = revenue_difference / revenue_se if revenue_se else 0.0
    revenue_p_value = float(2 * (1 - normal.cdf(abs(revenue_z))))
    revenue_noninferiority_floor = -0.05 * control_rpu

    if p_value < alpha and lift > 0 and revenue_ci[0] >= revenue_noninferiority_floor:
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
        revenue_difference=revenue_difference,
        revenue_relative_change=revenue_relative_change,
        revenue_confidence_interval=revenue_ci,
        revenue_p_value=revenue_p_value,
        recommendation=recommendation,
    )
