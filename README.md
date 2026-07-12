# MetricLab

MetricLab is an e-commerce experimentation and product analytics platform. It
turns event-level customer behavior into trustworthy experiment results and a
clear product recommendation.

The first use case evaluates whether a simplified checkout experience improves
purchase conversion without reducing revenue per user.

## What is implemented

- A pre-registered experiment specification in `docs/experiment_spec.md`
- A real, ordered January 2021 session funnel queried from Google's public GA4 sample
- Deterministic synthetic user-level e-commerce data
- Stable user-level treatment assignment
- Conversion lift, confidence intervals, p-values, and revenue guardrails
- A Streamlit results page
- Unit tests for the statistical core

The dashboard separates observed funnel metrics from simulated experiment
results. The simulated treatment effect is explicitly labeled and is not
evidence about a real checkout redesign.

## Quick start

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
streamlit run app/streamlit_app.py
```

Run tests with:

```bash
python -m unittest discover -s tests -v
```

## Roadmap

1. Add power analysis and sample-ratio-mismatch detection.
2. Add CUPED variance reduction.
3. Add segment analysis and automated data-quality checks.
4. Publish an executive experiment readout and deploy the dashboard.
