# Experiment plan — predeclared in the project, not field-tested

**Problem:** discounted special event bundle might raise payer conversion but lower IAP revenue per randomized eligible user.

**Hypothesis:** price change $4.99 → $3.99 increases bundle purchases. This does not guarantee total monetization improves.

**Randomization:** 12,000 synthetic, event-eligible entrants; 50/50 assigned *before* simulation; one treatment variable, special bundle price.

**Time window:** 14-day event; a 7-day follow-up used only for descriptive bounded RPU/return. All users were eligible and active on day 1 by construction.

**Primary success KPI:** 14-day all-IAP revenue per assigned user (ITT). 95% player-bootstrap CI lower bound of Difference (Discount − Control) must be strictly above zero.

**Guardrails:** D7 exact-day return delta lower 95% CI ≥ −1.5 pp and event completion delta lower 95% CI ≥ −2.0 pp.

**Secondary:** all-payer conversion, bundle purchase conversion, ARPPU, ARPDAU, cohort 21-day RPU, segment differences and monetization composition. Descriptive or exploratory only.

**Outcome policy:** `SIMULATED GO` only if all three criteria pass; otherwise `SIMULATED HOLD`. Neither label authorizes launch in a live game.

**Known modeling limitation:** retention is not directly driven by treatment in the synthetic generator; passing D7 guardrails is not proof that pricing is harmless.
