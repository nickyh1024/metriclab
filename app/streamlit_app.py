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

st.set_page_config(
    page_title="MetricLab | Product Experimentation",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp { background: #F6F8FB; }
    .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 4rem; }
    .metriclab-hero {
        background: linear-gradient(120deg, #111C35 0%, #183B50 62%, #0F766E 100%);
        border-radius: 22px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 1.35rem;
        box-shadow: 0 18px 45px rgba(15, 29, 55, 0.16);
        color: white;
    }
    .metriclab-eyebrow {
        color: #7DE3D2;
        font-size: 0.74rem;
        font-weight: 750;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }
    .metriclab-title {
        font-size: 2.7rem;
        line-height: 1.05;
        font-weight: 780;
        letter-spacing: -0.045em;
        margin: 0;
    }
    .metriclab-subtitle {
        color: #D7E4EA;
        font-size: 1.02rem;
        margin: 0.7rem 0 1.15rem 0;
        max-width: 720px;
    }
    .metriclab-pill {
        display: inline-block;
        color: #D8FFF8;
        background: rgba(15, 157, 138, 0.22);
        border: 1px solid rgba(125, 227, 210, 0.32);
        border-radius: 999px;
        padding: 0.32rem 0.68rem;
        margin: 0 0.35rem 0.2rem 0;
        font-size: 0.76rem;
        font-weight: 650;
    }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E3E9F0;
        border-radius: 14px;
        padding: 1rem 1.05rem;
        box-shadow: 0 5px 18px rgba(23, 32, 51, 0.045);
    }
    div[data-testid="stMetricLabel"] { color: #64748B; }
    div[data-testid="stMetricValue"] { color: #172033; font-weight: 720; }
    div[data-testid="stTabs"] button { font-weight: 650; }
    div[data-testid="stAlert"] { border-radius: 13px; }
    div[data-testid="stExpander"] {
        background: #FFFFFF;
        border-color: #E3E9F0;
        border-radius: 13px;
    }
    .section-kicker {
        color: #0F766E;
        font-size: 0.73rem;
        font-weight: 750;
        letter-spacing: 0.11em;
        text-transform: uppercase;
        margin: 1.4rem 0 0.25rem 0;
    }
    .section-title {
        color: #172033;
        font-size: 1.55rem;
        font-weight: 730;
        letter-spacing: -0.025em;
        margin: 0 0 0.75rem 0;
    }
    .decision-card {
        background: linear-gradient(110deg, #FFF8E7 0%, #FFFFFF 75%);
        border: 1px solid #F3D995;
        border-left: 6px solid #E8A317;
        border-radius: 16px;
        padding: 1.15rem 1.3rem;
        margin: 0.6rem 0 1rem 0;
    }
    .decision-label {
        color: #8A5A00;
        font-size: 0.72rem;
        font-weight: 780;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .decision-value { color: #3D2A00; font-size: 1.65rem; font-weight: 780; }
    .decision-copy { color: #6B5631; font-size: 0.9rem; margin-top: 0.2rem; }
    </style>

    <div class="metriclab-hero">
      <div class="metriclab-eyebrow">Product analytics case study</div>
      <div class="metriclab-title">MetricLab</div>
      <div class="metriclab-subtitle">
        From customer behavior to a defensible product decision — using ordered
        funnel analysis, experiment design, and statistical guardrails.
      </div>
      <span class="metriclab-pill">BigQuery SQL</span>
      <span class="metriclab-pill">Experimentation</span>
      <span class="metriclab-pill">Statistical inference</span>
      <span class="metriclab-pill">Streamlit</span>
    </div>
    """,
    unsafe_allow_html=True,
)

funnel_tab, experiment_tab = st.tabs(["Real customer funnel", "Simulated experiment"])

with funnel_tab:
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Product-view sessions", "23,105")
    kpi2.metric("View → cart", "18.3%", "Primary opportunity", delta_color="off")
    kpi3.metric("View → purchase", "3.5%")
    kpi4.metric("Largest drop-off", "81.7%", "Before cart", delta_color="inverse")

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

    st.markdown(
        '<div class="section-kicker">Journey analysis</div>'
        '<div class="section-title">Where customers leave the funnel</div>',
        unsafe_allow_html=True,
    )

    funnel_chart = (
        alt.Chart(funnel)
        .mark_bar(cornerRadiusEnd=6, color="#0F9D8A", size=30)
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
        .properties(height=265)
        .configure_axis(
            labelColor="#526176",
            titleColor="#526176",
            gridColor="#E8EDF3",
            domain=False,
            tickColor="#D7DEE8",
        )
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
    st.markdown(
        "**Interpretation:** The clearest opportunity appears before cart addition. "
        "Only 18.3% of product-view sessions progress to the cart, motivating a "
        "product-page experiment rather than an immediate redesign."
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
        acquisition_chart = (
            alt.Chart(acquisition)
            .mark_bar(cornerRadiusEnd=5, color="#5372E7")
            .encode(
                x=alt.X("view_to_cart_rate:Q", title="View-to-cart rate", axis=alt.Axis(format=".0%")),
                y=alt.Y("segment:N", title=None, sort="-x"),
                tooltip=[
                    alt.Tooltip("segment:N", title="Acquisition segment"),
                    alt.Tooltip("viewed_item_sessions:Q", title="Sessions", format=","),
                    alt.Tooltip("view_to_cart_rate:Q", title="View-to-cart", format=".1%"),
                ],
            )
            .properties(height=285)
        )
        st.altair_chart(acquisition_chart, width="stretch")
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

    st.markdown(
        '<div class="section-kicker">Plan</div>'
        '<div class="section-title">Size the experiment before reading results</div>',
        unsafe_allow_html=True,
    )
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

    st.markdown(
        '<div class="section-kicker">Validate</div>'
        '<div class="section-title">Confirm trustworthy assignment</div>',
        unsafe_allow_html=True,
    )
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

    st.markdown(
        '<div class="section-kicker">Decide</div>'
        '<div class="section-title">Translate evidence into action</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="decision-card">
          <div class="decision-label">Recommendation</div>
          <div class="decision-value">{result.recommendation}</div>
          <div class="decision-copy">
            The primary metric improved, but the revenue interval is still wide
            enough to include meaningful harm. Continue measurement before launch.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Control view-to-cart", f"{result.control_conversion:.2%}")
    col2.metric(
        "Treatment view-to-cart",
        f"{result.treatment_conversion:.2%}",
        f"{result.absolute_lift:.2%} absolute",
    )
    col3.metric("Relative lift", f"{result.relative_lift:.1%}")
    col4.metric("p-value", f"{result.p_value:.4f}")

    st.markdown("#### Primary-metric uncertainty")
    lower, upper = result.confidence_interval
    st.write(
        f"95% confidence interval for absolute lift: **{lower:.2%} to {upper:.2%}**"
    )

    st.markdown("#### Revenue guardrail")
    revenue = pd.DataFrame(
        {
            "Variant": ["Control", "Treatment"],
            "Revenue per session": [
                result.control_revenue_per_user,
                result.treatment_revenue_per_user,
            ],
        }
    )
    revenue_chart = (
        alt.Chart(revenue)
        .mark_bar(cornerRadiusEnd=6, size=34)
        .encode(
            x=alt.X("Revenue per session:Q", title="Revenue per session ($)"),
            y=alt.Y("Variant:N", title=None, sort=["Control", "Treatment"]),
            color=alt.Color(
                "Variant:N",
                scale=alt.Scale(domain=["Control", "Treatment"], range=["#64748B", "#0F9D8A"]),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("Variant:N"),
                alt.Tooltip("Revenue per session:Q", format="$.2f"),
            ],
        )
        .properties(height=135)
    )
    st.altair_chart(revenue_chart, width="stretch")
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
            - Randomization unit: eligible session
            - Allocation: 50/50 control and treatment
            - Primary metric: view-to-cart conversion per eligible session
            - Guardrail: revenue per eligible session
            - Test: two-sided two-proportion z-test at α = 0.05
            """
        )
