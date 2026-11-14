# The natural story — learn this, not a memorized script

1. **Problem:** a discount can raise conversion while reducing unit revenue.
2. **Design:** limited-time event, one experimental variable: $4.99 vs $3.99 bundle. Exactly 6,000 synthetic players per arm, randomized at launch.
3. **Model:** three assumed personas, stochastic participation, purchases, milestones and churn; organic purchases continue alongside the bundle.
4. **Data:** action-level logs, SQLite, ARPDAU/ARPPU and assigned-user conversion; reconcile dollars from events to user totals.
5. **Evidence:** in the simulated run, Discount increases payer conversion but does not lift IAP revenue per randomized user. Revenue interval spans zero.
6. **Decision:** rule rejects a simulated GO because primary metric uncertainty remains; engagement guardrails pass but have built-in limits.
7. **Professional judgment:** do not confuse simulation results with live evidence; instrument real purchase data, estimate demand/variance, then design and run a powered A/B test.

## How to defend the technical work

- **Python model** (`src/model.py`): assigns arms and executes per-player daily stochastic behavior.
- **Analysis** (`src/analyze.py`): aggregates to one user, bootstraps 95% paired-group comparison and applies predeclared gates.
- **SQL** (`sql/02_payer_funnel_by_variant.sql`): preserves the randomized denominator with `LEFT JOIN` instead of selecting only buyers.
- **Revenue QA** (`sql/04_revenue_reconciliation.sql`): checks every user's modeled revenue against their purchase events.
- **Sensitivity** (`src/pricing.py`): shows that preferred price can change when the assumed response curve changes. This is not empirical optimization.

**Integrity note:** If discussing authorship, be accurate about using AI development assistance. A defensible portfolio requires that you can explain the model, run it, inspect the outcomes, and be transparent about limitations.
