# View-to-Cart Segmentation Findings

## Device category

| Device | Product-view sessions | Cart sessions | View-to-cart rate |
|---|---:|---:|---:|
| Desktop | 13,438 | 2,438 | 18.1% |
| Mobile | 9,111 | 1,692 | 18.6% |
| Tablet | 556 | 93 | 16.7% |

Desktop and mobile conversion were similar. Tablet conversion was lower, but
the tablet sample was much smaller. These descriptive results do not support a
claim that mobile-specific friction explains the overall view-to-cart drop-off.

This is a useful negative finding: MetricLab should not recommend a mobile
redesign merely because mobile usability is a plausible hypothesis. Further
segmentation and statistical uncertainty checks are required.

## User acquisition source

| Acquisition source / medium | Product-view sessions | View-to-cart rate |
|---|---:|---:|
| Google / organic | 7,192 | 16.5% |
| Direct / none | 5,280 | 18.7% |
| Other / Other | 3,310 | 17.0% |
| Other / referral | 2,218 | 18.5% |
| Google Merchandise Store / referral | 1,918 | 21.6% |
| Data deleted | 1,526 | 25.8% |
| Google / CPC | 994 | 15.3% |
| Other / organic | 648 | 17.9% |

Paid Google traffic had the lowest observed view-to-cart rate among segments
with at least 100 product-view sessions. Direct traffic converted at a higher
rate. This pattern is consistent with differences in visitor intent, landing
page expectations, or campaign targeting, but the observational data cannot
identify which explanation is correct.

The acquisition fields use first-touch user attribution rather than current-
session attribution. The self-referral, `<Other>`, and deleted-data categories
also reveal attribution and obfuscation limitations. These groups should not be
used to make precise business claims.

## Resulting experiment direction

The analysis motivates testing clearer product-page information and calls to
action for product-view sessions. View-to-cart conversion remains the primary
metric. Acquisition source can be used as a diagnostic segment, but treatment
should be randomized across eligible sessions so the experiment can support a
causal conclusion.
