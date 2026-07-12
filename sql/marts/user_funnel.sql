-- Monthly user funnel from Google's public GA4 e-commerce sample.
-- BigQuery Standard SQL. Adjust the table suffixes to change the analysis month.

SELECT
  COUNT(DISTINCT user_pseudo_id) AS total_users,
  COUNT(DISTINCT IF(
    event_name = 'view_item', user_pseudo_id, NULL
  )) AS viewed_item_users,
  COUNT(DISTINCT IF(
    event_name = 'add_to_cart', user_pseudo_id, NULL
  )) AS added_to_cart_users,
  COUNT(DISTINCT IF(
    event_name = 'begin_checkout', user_pseudo_id, NULL
  )) AS began_checkout_users,
  COUNT(DISTINCT IF(
    event_name = 'purchase', user_pseudo_id, NULL
  )) AS purchased_users
FROM
  `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE
  _TABLE_SUFFIX BETWEEN '20210101' AND '20210131';

