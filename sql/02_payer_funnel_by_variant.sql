-- One row per assigned player in the experiment: ITT conversion denominator.
WITH paying AS (
 SELECT variant,user_id FROM events WHERE day<=14 AND revenue_usd>0 GROUP BY variant,user_id
), offer AS (
 SELECT variant,user_id FROM events WHERE day<=14 AND event_type='bundle_purchase' GROUP BY variant,user_id
), impressions AS (
 SELECT variant,user_id FROM events WHERE day<=14 AND event_type='bundle_impression' GROUP BY variant,user_id
)
SELECT u.variant,COUNT(*) AS assigned_users,
 COUNT(i.user_id) AS exposed_users,
 COUNT(p.user_id) AS paying_users,
 COUNT(o.user_id) AS bundle_buyers,
 ROUND(1.0*COUNT(p.user_id)/COUNT(*),4) AS payer_conversion_itt,
 ROUND(1.0*COUNT(o.user_id)/COUNT(*),4) AS bundle_conversion_itt
FROM users u
LEFT JOIN impressions i ON i.variant=u.variant AND i.user_id=u.user_id
LEFT JOIN paying p ON p.variant=u.variant AND p.user_id=u.user_id
LEFT JOIN offer o ON o.variant=u.variant AND o.user_id=u.user_id
GROUP BY u.variant ORDER BY u.variant;
