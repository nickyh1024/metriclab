# January 2021 Ordered Session Funnel

## Question

Where do shopping sessions experience the greatest loss before purchase?

## Results

| Stage | Sessions | Conversion from previous stage |
|---|---:|---:|
| Viewed item | 23,105 | 100.0% |
| Added to cart | 4,223 | 18.3% |
| Began checkout | 1,455 | 34.5% |
| Purchased | 811 | 55.7% |

Overall view-to-purchase conversion was 3.5%.

## Interpretation

The largest observed drop-off occurred between viewing a product and adding it
to the cart. This identifies a useful area for further investigation, but it
does not prove why users left or establish that a particular product change
would improve conversion.

MetricLab therefore uses this result to motivate an experiment rather than to
make a causal claim. Candidate hypotheses include unclear product information,
unexpected pricing, weak calls to action, or low purchase intent among some
traffic sources. Segment analysis should be used to narrow these hypotheses
before proposing a specific intervention.

## Method

The BigQuery analysis uses `user_pseudo_id` and the GA4 `ga_session_id`. A
session reaches a stage only when that event occurred after every preceding
stage in the same session. See `sql/marts/ordered_session_funnel.sql`.
