-- Ordered January 2021 shopping funnel from Google's public GA4 sample.
-- A session reaches a stage only when it completed every prior stage in order.

WITH events AS (
  SELECT
    user_pseudo_id,
    (
      SELECT value.int_value
      FROM UNNEST(event_params)
      WHERE key = 'ga_session_id'
    ) AS session_id,
    event_name,
    event_timestamp
  FROM
    `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE
    _TABLE_SUFFIX BETWEEN '20210101' AND '20210131'
    AND user_pseudo_id IS NOT NULL
),

-- Find the first product view in each eligible session.
views AS (
  SELECT
    user_pseudo_id,
    session_id,
    MIN(event_timestamp) AS viewed_at
  FROM events
  WHERE
    event_name = 'view_item'
    AND session_id IS NOT NULL
  GROUP BY user_pseudo_id, session_id
),

-- Find the first cart event occurring after that session's product view.
carts AS (
  SELECT
    views.user_pseudo_id,
    views.session_id,
    MIN(events.event_timestamp) AS added_to_cart_at
  FROM views
  INNER JOIN events
    ON views.user_pseudo_id = events.user_pseudo_id
    AND views.session_id = events.session_id
    AND events.event_name = 'add_to_cart'
    AND events.event_timestamp > views.viewed_at
  GROUP BY views.user_pseudo_id, views.session_id
),

-- Find the first checkout event occurring after the cart event.
checkouts AS (
  SELECT
    carts.user_pseudo_id,
    carts.session_id,
    MIN(events.event_timestamp) AS began_checkout_at
  FROM carts
  INNER JOIN events
    ON carts.user_pseudo_id = events.user_pseudo_id
    AND carts.session_id = events.session_id
    AND events.event_name = 'begin_checkout'
    AND events.event_timestamp > carts.added_to_cart_at
  GROUP BY carts.user_pseudo_id, carts.session_id
),

-- Find the first purchase occurring after checkout in that same session.
purchases AS (
  SELECT
    checkouts.user_pseudo_id,
    checkouts.session_id,
    MIN(events.event_timestamp) AS purchased_at
  FROM checkouts
  INNER JOIN events
    ON checkouts.user_pseudo_id = events.user_pseudo_id
    AND checkouts.session_id = events.session_id
    AND events.event_name = 'purchase'
    AND events.event_timestamp > checkouts.began_checkout_at
  GROUP BY checkouts.user_pseudo_id, checkouts.session_id
)

SELECT
  COUNT(*) AS viewed_item_sessions,
  COUNT(carts.session_id) AS added_to_cart_sessions,
  COUNT(checkouts.session_id) AS began_checkout_sessions,
  COUNT(purchases.session_id) AS purchased_sessions,
  SAFE_DIVIDE(COUNT(carts.session_id), COUNT(*)) AS view_to_cart_rate,
  SAFE_DIVIDE(COUNT(checkouts.session_id), COUNT(carts.session_id))
    AS cart_to_checkout_rate,
  SAFE_DIVIDE(COUNT(purchases.session_id), COUNT(checkouts.session_id))
    AS checkout_to_purchase_rate,
  SAFE_DIVIDE(COUNT(purchases.session_id), COUNT(*))
    AS overall_funnel_conversion
FROM views
LEFT JOIN carts USING (user_pseudo_id, session_id)
LEFT JOIN checkouts USING (user_pseudo_id, session_id)
LEFT JOIN purchases USING (user_pseudo_id, session_id);
