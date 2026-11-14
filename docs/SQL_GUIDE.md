# SQL guide — six analytical questions

Tables created by `python -m src.run_analysis`:

- `users`: one randomized user (`user_id`) per row. Contains variant, persona, assigned price, completion, total IAP revenue, prior-week activity proxy, and synthetic behavior propensities.
- `events`: one recorded action per row; contains `event_id`, `user_id`, `variant`, `persona`, `day`, `event_type`, `revenue_usd`, and `milestones`.

**Keys:** `users.user_id` uniquely identifies the assigned player. The `events.user_id` foreign key is repeated once per action; join aggregation by user, not directly join raw events to users when counting people.

| Query | Question | Main SQL idea |
|---|---|---|
| `01_daily_arpdau.sql` | How much purchase revenue per active user each day? | `GROUP BY variant,day`, `COUNT(DISTINCT user_id)`, join daily totals |
| `02_payer_funnel_by_variant.sql` | How many assigned users saw the offer, paid or bought the bundle? | user-level deduplicated subqueries, `LEFT JOIN` to full randomized denominator |
| `03_segment_liveops_performance.sql` | Are conversion and engagement different by persona? | grouped `AVG` with explicit `COALESCE` |
| `04_revenue_reconciliation.sql` | Do purchase events explain all stored user revenue? | `SUM`, `LEFT JOIN`, row-wise difference must be 0 |
| `05_retention_by_variant.sql` | How many originally randomized users played on event days 7, 14, 21? | exact-day activity and fixed assigned denominator |
| `06_price_offer_revenue.sql` | How much revenue comes from special bundles vs ordinary IAP? | conditional `SUM` and distinct user counts |

**Important:** `SELECT AVG(revenue_usd)` on raw events is *not* the same as revenue per randomized user: it uses event rows, not users, as its denominator. For experiment results, aggregate to one player first or join to a table containing every assigned player.

Queries produce six CSV files in `reports/` after running the pipeline.
