-- Every USD recorded on user outcome must be explainable by purchase events.
WITH ledger AS (
 SELECT user_id,ROUND(SUM(revenue_usd),2) AS recorded_revenue
 FROM events GROUP BY user_id
)
SELECT u.user_id,u.variant,u.revenue_usd_21,
 COALESCE(l.recorded_revenue,0) AS ledger_revenue,
 ROUND(u.revenue_usd_21-COALESCE(l.recorded_revenue,0),8) AS revenue_difference
FROM users u LEFT JOIN ledger l ON u.user_id=l.user_id ORDER BY u.user_id;
