# LiveOps price A/B — synthetic decision memo

## Decision question
Does a 20% discounted $3.99 event bundle improve 14-day in-app-purchase revenue per randomized event-eligible user versus $4.99, while respecting engagement guardrails?

## Preregistered success criterion (demonstration)
Primary: 14-day IAP RPU (including organic IAP). Require bootstrap 95% CI of Discount minus Control entirely above zero. Guardrails: D7 exact return lower 95% CI ≥ −1.5 pp; event completion lower 95% CI ≥ −2 pp.

## Results — simulated only

| Metric | Control | Discount | Difference | Bootstrap CI |
|---|---:|---:|---:|---:|
| iap_rpu_d14 | 0.9418 | 0.9032 | -0.0386 | [-0.1041, 0.0362] |
| payer_d14 | 0.1935 | 0.2195 | 0.0260 | [0.0103, 0.0408] |
| bundle_purchased | 0.1440 | 0.1667 | 0.0227 | [0.0097, 0.0345] |
| d7_return | 0.4452 | 0.4490 | 0.0038 | [-0.0135, 0.0208] |
| event_completion | 0.2978 | 0.3012 | 0.0033 | [-0.0127, 0.0190] |

**Decision under synthetic demonstration rule: SIMULATED HOLD**

Guardrails:
- primary_revenue_lower_ci_positive: False
- d7_guardrail_lower_ci_at_least_minus_1_5pp: True
- event_completion_lower_ci_at_least_minus_2pp: True

## How to interpret correctly
- Random assignment is genuine in the simulator, but outcomes follow assumed behavioral probabilities; this is **not** a live-game A/B test.
- Only the bundle price differs by arm; event milestones and organic offer behavior are held fixed.
- Conversion can move differently from IAP revenue per randomized user because lower prices reduce revenue per purchase.
- Bootstrap CI and p-values quantify simulation sampling variability, **not** external validity or evidence about players in the real world.
- Event completion and return are not directly affected by price in model rules; their stability is largely built in.
- The pricing grid is a counterfactual assumption sensitivity analysis, not an empirically estimated revenue-maximizing price.
- 21-day revenue per user is a finite-window RPU proxy, **not** modeled lifetime LTV.
- Assumed player-level latent propensities and personas are not fitted to real data; price elasticity, engagement, fairness and longer-run impacts require observation and experiments.

## Practical next steps for a real studio
1. Validate instrumentation, purchase integrity, refunds/currency, targeting and exposure eligibility.
2. Calibrate funnel dropoff, IAP price sensitivity and retention by level/tenure/geography using actual data.
3. Pre-register primary metric and guardrails, size the experiment and ensure no overlapping live promotions.
4. Run ethical randomized test, monitor adverse signals, and decide only on measured outcomes.
