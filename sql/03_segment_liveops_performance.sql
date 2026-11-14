-- Segment outcomes by original randomized assignment, not selected payers.
WITH paid AS (
 SELECT variant,user_id,SUM(revenue_usd) AS revenue14
 FROM events WHERE day<=14 GROUP BY variant,user_id
), d7 AS (
 SELECT variant,user_id FROM events WHERE event_type='session_start' AND day=7
)
SELECT u.variant,u.persona,COUNT(*) AS assigned_users,
 ROUND(AVG(COALESCE(p.revenue14,0)),4) AS rpu_d14,
 ROUND(AVG(CASE WHEN COALESCE(p.revenue14,0)>0 THEN 1.0 ELSE 0 END),4) AS payer_conversion,
 ROUND(AVG(CASE WHEN d7.user_id IS NOT NULL THEN 1.0 ELSE 0 END),4) AS d7_return,
 ROUND(AVG(u.event_completed),4) AS event_completion
FROM users u LEFT JOIN paid p ON p.user_id=u.user_id AND p.variant=u.variant
LEFT JOIN d7 ON d7.user_id=u.user_id AND d7.variant=u.variant
GROUP BY u.variant,u.persona ORDER BY u.variant,u.persona;
