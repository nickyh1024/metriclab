-- Compare ordered view-to-cart conversion by user acquisition source/medium.
-- traffic_source describes the source that first acquired the user; it is not
-- necessarily the source of the current session.

WITH events AS (
  SELECT
    user_pseudo_id,
    (
      SELECT value.int_value
      FROM UNNEST(event_params)
      WHERE key = 'ga_session_id'
    ) AS session_id,
    COALESCE(traffic_source.source, '(unknown)') AS acquisition_source,
    COALESCE(traffic_source.medium, '(unknown)') AS acquisition_medium,
    event_name,
    event_timestamp
  FROM
    `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE
    _TABLE_SUFFIX BETWEEN '20210101' AND '20210131'
    AND user_pseudo_id IS NOT NULL
),

views AS (
  SELECT
    user_pseudo_id,
    session_id,
    acquisition_source,
    acquisition_medium,
    MIN(event_timestamp) AS viewed_at
  FROM events
  WHERE
    event_name = 'view_item'
    AND session_id IS NOT NULL
  GROUP BY
    user_pseudo_id,
    session_id,
    acquisition_source,
    acquisition_medium
),

carts AS (
  SELECT
    views.user_pseudo_id,
    views.session_id,
    views.acquisition_source,
    views.acquisition_medium,
    MIN(events.event_timestamp) AS added_to_cart_at
  FROM views
  INNER JOIN events
    ON views.user_pseudo_id = events.user_pseudo_id
    AND views.session_id = events.session_id
    AND events.event_name = 'add_to_cart'
    AND events.event_timestamp > views.viewed_at
  GROUP BY
    views.user_pseudo_id,
    views.session_id,
    views.acquisition_source,
    views.acquisition_medium
),

segment_results AS (
  SELECT
    views.acquisition_source,
    views.acquisition_medium,
    COUNT(*) AS viewed_item_sessions,
    COUNT(carts.session_id) AS added_to_cart_sessions,
    SAFE_DIVIDE(COUNT(carts.session_id), COUNT(*)) AS view_to_cart_rate
  FROM views
  LEFT JOIN carts USING (
    user_pseudo_id,
    session_id,
    acquisition_source,
    acquisition_medium
  )
  GROUP BY views.acquisition_source, views.acquisition_medium
)

SELECT *
FROM segment_results
WHERE viewed_item_sessions >= 100
ORDER BY viewed_item_sessions DESC;
