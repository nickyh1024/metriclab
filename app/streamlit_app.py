"""MetricLab's product funnel and experiment results page."""

from pathlib import Path

import pandas as pd
import streamlit as st

from metriclab import analyze_experiment, simulate_checkout_experiment

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

    st.bar_chart(funnel.set_index("stage")["sessions"], horizontal=True)
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
        use_container_width=True,
    )
    st.metric("Overall view-to-purchase conversion", "3.5%")
    st.markdown(
        "**Primary opportunity:** only 18.3% of sessions with a product view "
        "progress to adding an item to the cart."
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

    with st.sidebar:
        st.header("Simulation settings")
        users = st.slider("Eligible users", 2_000, 100_000, 20_000, step=2_000)
        baseline = st.slider("Baseline conversion", 0.02, 0.40, 0.12, step=0.01)
        effect = st.slider("Absolute treatment effect", -0.03, 0.05, 0.012, step=0.001)
        seed = st.number_input("Random seed", min_value=0, value=42, step=1)

    data = simulate_checkout_experiment(users, baseline, effect, int(seed))
    result = analyze_experiment(data)

    st.subheader("Decision")
    st.markdown(f"## {result.recommendation}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Control conversion", f"{result.control_conversion:.2%}")
    col2.metric(
        "Treatment conversion",
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
