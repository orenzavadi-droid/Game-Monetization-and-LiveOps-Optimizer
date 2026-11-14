-- Daily IAP revenue per unique daily active user (in this synthetic game).
WITH dau AS (
 SELECT variant,day,COUNT(DISTINCT user_id) AS active_users
 FROM events WHERE event_type='session_start' AND day<=14
 GROUP BY variant,day
), money AS (
 SELECT variant,day,ROUND(SUM(revenue_usd),2) AS iap_revenue
 FROM events WHERE day<=14
 GROUP BY variant,day
)
SELECT d.variant,d.day,d.active_users,COALESCE(m.iap_revenue,0) AS iap_revenue,
 ROUND(COALESCE(m.iap_revenue,0)/NULLIF(d.active_users,0),5) AS arpdau_usd
FROM dau d LEFT JOIN money m ON d.variant=m.variant AND d.day=m.day
ORDER BY d.variant,d.day;
