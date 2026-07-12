# MetricLab Experiment Decision Memo

## Recommendation: Iterate

Do not ship the proposed product-page treatment yet. The simulated experiment
shows a convincing improvement in view-to-cart conversion, but the downstream
revenue guardrail is too imprecise to rule out meaningful harm.

## Planned experiment

- **Control:** Existing product page
- **Treatment:** Clearer product information and stronger add-to-cart call to action
- **Primary metric:** View-to-cart conversion per eligible session
- **Guardrail:** Revenue per eligible session
- **Allocation:** 50% control / 50% treatment
- **Simulated eligible sessions:** 20,000

## Assignment validation

- Control: 9,938 sessions
- Treatment: 10,062 sessions
- Sample-ratio-mismatch p-value: 0.381
- Result: Pass

The observed allocation is consistent with ordinary random variation.

## Primary result

- Control view-to-cart rate: 18.21%
- Treatment view-to-cart rate: 20.16%
- Absolute lift: 1.94 percentage points
- Relative lift: 10.66%
- 95% confidence interval: 0.85 to 3.03 percentage points
- p-value: < 0.001

The primary metric improved by a statistically significant and practically
meaningful amount in the simulation.

## Revenue guardrail

- Control revenue per session: $2.88
- Treatment revenue per session: $2.67
- Relative change: -7.46%
- Difference: -$0.22 per session
- 95% confidence interval for the difference: -$0.66 to $0.23
- p-value: 0.346

The revenue difference is not statistically significant, but its confidence
interval includes both meaningful harm and a modest benefit. Therefore, the
experiment does not yet demonstrate that the treatment is safe for revenue.

## Next action

Continue the experiment or increase guardrail sensitivity before launch. A
real product team should also inspect downstream checkout completion, average
order value, and tracking quality. Ship only after the primary lift remains
credible and the revenue guardrail rules out the agreed non-inferiority margin.

## Simulation disclosure

These outcomes are simulated. MetricLab injects a 1.7 percentage-point effect
into view-to-cart conversion and no effect into revenue. The memo demonstrates
the decision process and intentionally does not claim a real product impact.
