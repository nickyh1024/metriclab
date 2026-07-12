"""MetricLab's product funnel and experiment results page."""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from metriclab import (
    analyze_experiment,
    check_assignment_balance,
    simulate_product_page_experiment,
    two_proportion_sample_size,
)

st.set_page_config(page_title="MetricLab", page_icon="📐", layout="wide")
st.title("MetricLab")
st.caption("E-commerce experimentation and product analytics")

funnel_tab, experiment_tab = st.tabs(["Real customer funnel", "Simulated experiment"])

with funnel_tab:
    st.info(
        "Observed January 2021 ordered session counts from Google's public, "
        "obfuscated GA4 e-commerce sample. These are descriptive metrics, not "
        "experiment results."
    )
    data_path = (
        Path(__file__).parents[1]
        / "data"
        / "sample"
        / "ordered_session_funnel_2021_01.csv"
    )
    funnel = pd.read_csv(data_path)

    funnel_chart = (
        alt.Chart(funnel)
        .mark_bar(cornerRadiusEnd=5, color="#2563EB")
        .encode(
            x=alt.X("sessions:Q", title="Sessions"),
            y=alt.Y(
                "stage:N",
                title=None,
                sort=["Viewed item", "Added to cart", "Began checkout", "Purchased"],
            ),
            tooltip=[
                alt.Tooltip("stage:N", title="Stage"),
                alt.Tooltip("sessions:Q", title="Sessions", format=","),
                alt.Tooltip(
                    "conversion_from_previous_stage:Q",
                    title="Previous-stage conversion",
                    format=".1%",
                ),
            ],
        )
        .properties(height=250)
    )
    st.altair_chart(funnel_chart, width="stretch")
    display = funnel.copy()
    display["conversion_from_previous_stage"] = display[
        "conversion_from_previous_stage"
    ].map("{:.1%}".format)
    st.dataframe(
        display.rename(
            columns={
                "stage": "Stage",
                "sessions": "Sessions",
                "conversion_from_previous_stage": "Conversion from previous stage",
            }
        ),
        hide_index=True,
        width="stretch",
    )
    st.metric("Overall view-to-purchase conversion", "3.5%")
    st.markdown(
        "**Primary opportunity:** only 18.3% of sessions with a product view "
        "progress to adding an item to the cart."
    )
    with st.expander("Acquisition segment detail"):
        acquisition_path = (
            Path(__file__).parents[1]
            / "data"
            / "sample"
            / "view_to_cart_by_acquisition_2021_01.csv"
        )
        acquisition = pd.read_csv(acquisition_path)
        acquisition["segment"] = (
            acquisition["acquisition_source"]
            + " / "
            + acquisition["acquisition_medium"]
        )
        st.bar_chart(
            acquisition.set_index("segment")["view_to_cart_rate"],
            horizontal=True,
        )
        st.caption(
            "First-touch acquisition segments are descriptive, not randomized. "
            "Differences may reflect visitor intent, attribution quality, or other factors."
        )
    st.caption(
        "Source query: sql/marts/ordered_session_funnel.sql. Each later stage "
        "must occur after the previous stage in the same user session."
    )

with experiment_tab:
    st.warning(
        "Simulation mode: the treatment effect below is injected for demonstration "
        "and is not a real causal finding."
    )

    with st.expander("Simulation settings", expanded=False):
        setting_col1, setting_col2 = st.columns(2)
        with setting_col1:
            users = st.slider(
                "Eligible sessions", 2_000, 100_000, 20_000, step=2_000
            )
            baseline = st.slider(
                "Baseline conversion", 0.02, 0.40, 0.183, step=0.001
            )
        with setting_col2:
            effect = st.slider(
                "Absolute treatment effect", -0.03, 0.05, 0.017, step=0.001
            )
            seed = st.number_input("Random seed", min_value=0, value=42, step=1)

    st.subheader("Experiment planning")
    planning_col1, planning_col2 = st.columns(2)
    planned_lift = planning_col1.slider(
        "Minimum detectable absolute lift",
        min_value=0.005,
        max_value=0.05,
        value=0.017,
        step=0.001,
        format="%.3f",
    )
    eligible_sessions_per_day = planning_col2.number_input(
        "Expected eligible sessions per day",
        min_value=100,
        value=750,
        step=50,
    )
    plan = two_proportion_sample_size(0.183, planned_lift)
    estimated_days = plan.total_users / eligible_sessions_per_day

    plan_col1, plan_col2, plan_col3 = st.columns(3)
    plan_col1.metric("Sessions per variant", f"{plan.users_per_variant:,}")
    plan_col2.metric("Total sessions", f"{plan.total_users:,}")
    plan_col3.metric("Estimated duration", f"{estimated_days:.1f} days")
    st.caption(
        f"Designed to detect a change from {plan.baseline_rate:.1%} to "
        f"{plan.target_rate:.1%} with {plan.power:.0%} power at a two-sided "
        f"{plan.alpha:.0%} significance level."
    )

    data = simulate_product_page_experiment(users, baseline, effect, seed=int(seed))
    balance = check_assignment_balance(data)
    result = analyze_experiment(data)

    st.subheader("Assignment quality")
    balance_col1, balance_col2, balance_col3 = st.columns(3)
    balance_col1.metric("Control sessions", f"{balance.control_users:,}")
    balance_col2.metric("Treatment sessions", f"{balance.treatment_users:,}")
    balance_col3.metric(
        "Balance check",
        "Pass" if balance.passed else "Fail",
        f"p = {balance.p_value:.4f}",
    )
    if not balance.passed:
        st.error(
            "The assignment split is suspicious. Investigate randomization or "
            "tracking before interpreting experiment outcomes."
        )

    st.subheader("Decision")
    st.markdown(f"## {result.recommendation}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Control view-to-cart", f"{result.control_conversion:.2%}")
    col2.metric(
        "Treatment view-to-cart",
        f"{result.treatment_conversion:.2%}",
        f"{result.absolute_lift:.2%} absolute",
    )
    col3.metric("Relative lift", f"{result.relative_lift:.1%}")
    col4.metric("p-value", f"{result.p_value:.4f}")

    st.subheader("Uncertainty")
    lower, upper = result.confidence_interval
    st.write(
        f"95% confidence interval for absolute lift: **{lower:.2%} to {upper:.2%}**"
    )

    st.subheader("Revenue guardrail")
    revenue = {
        "Control": result.control_revenue_per_user,
        "Treatment": result.treatment_revenue_per_user,
    }
    st.bar_chart(revenue, horizontal=True)
    st.caption(
        f"Treatment revenue per session changed by "
        f"{result.revenue_relative_change:+.1%}. The simulated treatment has no "
        "injected revenue effect, so observed differences are sampling noise."
    )
    revenue_lower, revenue_upper = result.revenue_confidence_interval
    st.write(
        "95% confidence interval for the revenue-per-session difference: "
        f"**${revenue_lower:.2f} to ${revenue_upper:.2f}** "
        f"(p = {result.revenue_p_value:.3f})."
    )

    with st.expander("Experiment design"):
        st.markdown(
            """
            - Randomization unit: user
            - Allocation: 50/50 control and treatment
            - Primary metric: purchase conversion per eligible user
            - Guardrail: revenue per eligible user
            - Test: two-sided two-proportion z-test at α = 0.05
            """
        )
