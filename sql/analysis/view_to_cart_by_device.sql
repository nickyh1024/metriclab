-- Compare ordered view-to-cart conversion by device category.
-- A cart counts only when it occurs after a product view in the same session.

WITH events AS (
  SELECT
    user_pseudo_id,
    (
      SELECT value.int_value
      FROM UNNEST(event_params)
      WHERE key = 'ga_session_id'
    ) AS session_id,
    device.category AS device_category,
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
    device_category,
    MIN(event_timestamp) AS viewed_at
  FROM events
  WHERE
    event_name = 'view_item'
    AND session_id IS NOT NULL
  GROUP BY user_pseudo_id, session_id, device_category
),

carts AS (
  SELECT
    views.user_pseudo_id,
    views.session_id,
    views.device_category,
    MIN(events.event_timestamp) AS added_to_cart_at
  FROM views
  INNER JOIN events
    ON views.user_pseudo_id = events.user_pseudo_id
    AND views.session_id = events.session_id
    AND events.event_name = 'add_to_cart'
    AND events.event_timestamp > views.viewed_at
  GROUP BY views.user_pseudo_id, views.session_id, views.device_category
)

SELECT
  views.device_category,
  COUNT(*) AS viewed_item_sessions,
  COUNT(carts.session_id) AS added_to_cart_sessions,
  SAFE_DIVIDE(COUNT(carts.session_id), COUNT(*)) AS view_to_cart_rate
FROM views
LEFT JOIN carts
  USING (user_pseudo_id, session_id, device_category)
GROUP BY views.device_category
ORDER BY viewed_item_sessions DESC;
