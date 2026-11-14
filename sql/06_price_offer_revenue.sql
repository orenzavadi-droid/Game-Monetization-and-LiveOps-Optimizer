-- Offer buyers and offer revenue separate from organic IAP revenue.
SELECT variant,
 COUNT(DISTINCT CASE WHEN event_type='bundle_impression' THEN user_id END) AS seen_offer,
 COUNT(DISTINCT CASE WHEN event_type='bundle_purchase' THEN user_id END) AS bundle_buyers,
 ROUND(SUM(CASE WHEN event_type='bundle_purchase' THEN revenue_usd ELSE 0 END),2) AS bundle_revenue,
 ROUND(SUM(CASE WHEN event_type='organic_purchase' THEN revenue_usd ELSE 0 END),2) AS organic_revenue
FROM events WHERE day<=14
GROUP BY variant ORDER BY variant;
