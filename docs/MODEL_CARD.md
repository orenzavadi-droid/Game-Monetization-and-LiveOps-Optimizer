# Model Card — Synthetic LiveOps bundle-price experiment

## Design
- Event-eligible synthetic 12,000 players, randomized 6,000 vs 6,000 on event day 1.
- All entrants start day 1 active by design. This is an **event-launch cohort**, not an install cohort.
- Event days 1–14, follow-up days 15–21.
- Control and Discount differ only in the special bundle's USD price (4.99 vs 3.99). No treatment-specific content, offers, or direct retention effect.
- Existing organic in-app purchases are possible on all days at a fixed $2.99.
- Segment probabilities (Casual 50%, Regular 35%, Enthusiast 15%) are assumptions, not identified from records.

| Assumption | Casual | Regular | Enthusiast |
|---|---:|---:|---:|
| Conditional daily play (before individual latent multiplier) | .46 | .63 | .79 |
| Churn hazard per surviving day | .048 | .032 | .022 |
| Event join per active day | .55 | .70 | .84 |
| Bundle base buy probability per eligible exposure/day | .014 | .026 | .048 |
| Organic IAP probability per active day | .007 | .012 | .020 |
| Assumed price sensitivity exponent | .65 | .95 | 1.20 |

## Offer price response
`p_day = clip(base_segment_buy_probability × spend_latent × (4.99 / offered_price) ^ price_sensitivity_segment, 0, 0.5)`.

`spend_latent` is a synthetic positive player random effect. Pricing sensitivity is **not learned** from player logs. The odds and mathematical form are illustrative, and should not be mistaken for elasticity inferred from a real experiment.

## Event mechanics
- Each active user can choose to participate in a limited-time event. Participants earn one milestone plus a chance of a second.
- An event is completed on accumulating 8 milestones in days 1–14.
- The special bundle is visible on active event days until purchased, and can be purchased at most once.
- Independent ordinary IAP purchases ($2.99) can occur on any active day.
- Day-level activity and churn do **not** depend directly on bundle price or whether it was purchased. Guardrail stability is thus at least partly **built into the model**.

## KPI taxonomy
| KPI | Exact numerator / denominator | Interpretation |
|---|---|---|
| `IAP RPU14` PRIMARY | All IAP revenue day 1–14 / **all randomized users** in variant | Dollars per assigned event-eligible user |
| `Payer conversion14` | Unique randomized users with ≥1 IAP day 1–14 / all randomized in variant | ITT payer rate |
| `Bundle conversion14` | Unique users with bundle purchase / all randomized in variant | ITT special bundle rate |
| `Daily ARPDAU` | Total IAP revenue on day / distinct users active on that day | Daily active-player denominator, not primary experiment metric |
| `ARPPU14` | Total IAP day 1–14 / unique payers day 1–14 | Spend per paying user, can fall when more low-price buyers enter |
| `D7 return` | Users active on event day 7 / all originally randomized in variant | Event-day exact-day return, not D7 after install |
| `Event completion` | Users with ≥8 earned event milestones / randomized variant users | Designed event engagement proxy |
| `Cohort RPU21` | IAP day 1–21 / randomized variant users | **Not** total lifetime value |

## Statistical analysis
- Primary metric registered before reading synthetic outcomes: IAP RPU14.
- Player (not session/day) is the sampling unit; bootstrap 1,000 independent resamples per arm for a percentile 95% confidence interval of Discount minus Control.
- Secondary outcomes: payer conversion, bundle conversion; guardrails: D7 return, event completion.
- Simulated decision gate: primary 95% interval lower bound >0, D7 lower difference bound ≥−1.5 pp, event completion difference lower bound ≥−2 pp.
- Inferential results only quantify sampling noise given the **assumed synthetic data generating process**. They are not evidence of a real-world treatment effect.
- No adjustment for multiple secondary comparisons; do not promote exploratory secondary metrics to confirmatory claims.

## Price sensitivity extension
The price grid $3.49–$5.99 evaluates assumed daily purchase propensity at low/base/high sensitivity multipliers (0.65, 1.0, 1.5). It uses a fixed event-active-day exposure proxy for user opportunity. It is a **model-scenario illustration**, not an independently randomized multi-arm A/B test or a model fitted to real demand. Without reliable price sensitivity, a revenue-maximizing price cannot be established.

## Limitations, biases and what next
- No user acquisition, payback/ROAS, ads, multi-currency, refunds/taxes, real store economics, country/payment differences or real welfare measure.
- Randomized trial *in simulation* isolates one change, but does not identify actual causal impact in a studio.
- Assignment is balanced 50/50; persona counts can differ by chance, so segment descriptive comparisons are exploratory.
- A user can join the event on a day but buy the offer even if they did not participate that day, as long as they were active and eligible.
- Need observed instrumentation, power analysis for real revenue variance, platform rules, meaningful retention/engagement safeguards, and live randomized testing.
