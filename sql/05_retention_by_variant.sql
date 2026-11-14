-- Exact-day return: numerator = assigned players active on day N.
WITH activity AS (
 SELECT variant,user_id,
 MAX(CASE WHEN day=7 THEN 1 ELSE 0 END) AS active_d7,
 MAX(CASE WHEN day=14 THEN 1 ELSE 0 END) AS active_d14,
 MAX(CASE WHEN day=21 THEN 1 ELSE 0 END) AS active_d21
 FROM events WHERE event_type='session_start' GROUP BY variant,user_id
)
SELECT u.variant,COUNT(*) AS randomized_users,
 ROUND(AVG(COALESCE(a.active_d7,0)),4) AS d7,
 ROUND(AVG(COALESCE(a.active_d14,0)),4) AS d14,
 ROUND(AVG(COALESCE(a.active_d21,0)),4) AS d21
FROM users u LEFT JOIN activity a ON u.variant=a.variant AND u.user_id=a.user_id
GROUP BY u.variant ORDER BY u.variant;
