"""One-command reproducible pipeline for the synthetic LiveOps analytics portfolio."""
from pathlib import Path
import json,sqlite3
import pandas as pd
from src.model import ExperimentConfig,simulate,summarize,segment_summary
from src.analyze import user_metrics,compare_groups,decision
from src.pricing import pricing_sensitivity

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data';REPORTS=ROOT/'reports'

def run(cfg:ExperimentConfig=ExperimentConfig()):
    DATA.mkdir(exist_ok=True);REPORTS.mkdir(exist_ok=True)
    users,events,daily_model=simulate(cfg)
    summary,daily=summarize(users,events,cfg)
    seg=segment_summary(users,events,cfg.event_days)
    ux=user_metrics(users,events,cfg.event_days)
    compare=compare_groups(ux)
    verdict=decision(compare)
    sens=pricing_sensitivity(users,events,cfg.reference_price,cfg.event_days)
    dfs={"experiment_summary.csv":summary,"daily_arpdau.csv":daily,
         "segment_summary.csv":seg,"ab_uncertainty.csv":compare,"pricing_sensitivity.csv":sens,
         "users.csv":users,"events.csv":events,"daily_model.csv":daily_model}
    for fn,df in dfs.items():df.to_csv(DATA/fn,index=False)
    events.head(1000).to_csv(DATA/'events_sample.csv',index=False)
    with sqlite3.connect(DATA/'liveops.sqlite') as conn:
        users.to_sql("users",conn,index=False,if_exists="replace")
        events.to_sql("events",conn,index=False,if_exists="replace")
        conn.execute("CREATE UNIQUE INDEX ux_user_id ON users(user_id)")
        conn.execute("CREATE INDEX ix_events_user ON events(user_id)")
        conn.execute("CREATE INDEX ix_events_day ON events(variant,day,event_type)")
        for sql in sorted((ROOT/'sql').glob('*.sql')):
            q=pd.read_sql_query(sql.read_text(encoding='utf8'),conn)
            q.to_csv(REPORTS/f'{sql.stem}.csv',index=False)
        # independently audit all users and all dollar entries.
        audit=pd.read_sql_query((ROOT/'sql/04_revenue_reconciliation.sql').read_text(),conn)
        assert len(audit)==cfg.n_users
        assert (audit.revenue_difference.abs()<1e-7).all()
    (REPORTS/'decision.json').write_text(json.dumps(verdict,indent=2,ensure_ascii=False),encoding='utf-8')
    (REPORTS/'model_config.json').write_text(json.dumps(cfg.__dict__,indent=2),encoding='utf-8')
    # concise evidence report, not a causal claim about real players
    ix=compare.set_index('metric'); m=summary.set_index('variant')
    lines=["# LiveOps price A/B — synthetic decision memo","",
      "## Decision question","Does a 20% discounted $3.99 event bundle improve 14-day in-app-purchase revenue per randomized event-eligible user versus $4.99, while respecting engagement guardrails?","",
      "## Preregistered success criterion (demonstration)","Primary: 14-day IAP RPU (including organic IAP). Require bootstrap 95% CI of Discount minus Control entirely above zero. Guardrails: D7 exact return lower 95% CI ≥ −1.5 pp; event completion lower 95% CI ≥ −2 pp.","",
      "## Results — simulated only","", "| Metric | Control | Discount | Difference | Bootstrap CI |","|---|---:|---:|---:|---:|"]
    for metric in ["iap_rpu_d14","payer_d14","bundle_purchased","d7_return","event_completion"]:
        x=ix.loc[metric]; f=lambda v:f'{v:.4f}'
        lines.append(f'| {metric} | {f(x.control)} | {f(x.discount)} | {f(x.delta_discount_minus_control)} | [{f(x.ci_lower_95)}, {f(x.ci_upper_95)}] |')
    lines += ["",f"**Decision under synthetic demonstration rule: {verdict['decision']}**", "", "Guardrails:"]
    lines += [f"- {k}: {v}" for k,v in verdict['gates'].items()]
    lines += ["", "## How to interpret correctly", "- Random assignment is genuine in the simulator, but outcomes follow assumed behavioral probabilities; this is **not** a live-game A/B test.","- Only the bundle price differs by arm; event milestones and organic offer behavior are held fixed.","- Conversion can move differently from IAP revenue per randomized user because lower prices reduce revenue per purchase.","- Bootstrap CI and p-values quantify simulation sampling variability, **not** external validity or evidence about players in the real world.","- Event completion and return are not directly affected by price in model rules; their stability is largely built in.","- The pricing grid is a counterfactual assumption sensitivity analysis, not an empirically estimated revenue-maximizing price.","- 21-day revenue per user is a finite-window RPU proxy, **not** modeled lifetime LTV.","- Assumed player-level latent propensities and personas are not fitted to real data; price elasticity, engagement, fairness and longer-run impacts require observation and experiments.","", "## Practical next steps for a real studio","1. Validate instrumentation, purchase integrity, refunds/currency, targeting and exposure eligibility.","2. Calibrate funnel dropoff, IAP price sensitivity and retention by level/tenure/geography using actual data.","3. Pre-register primary metric and guardrails, size the experiment and ensure no overlapping live promotions.","4. Run ethical randomized test, monitor adverse signals, and decide only on measured outcomes."]
    (REPORTS/'DECISION_MEMO.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Events:',len(events),'users:',len(users),'reconciliation: PASS')
    print(summary[['variant','iap_rpu_usd_d14','payer_conversion_d14','bundle_conversion_d14','d7_return']].to_string(index=False))
    print('Decision:',verdict)
    return {'users':users,'events':events,'summary':summary,'daily':daily,'segment':seg,'comparison':compare,'pricing':sens,'decision':verdict}

if __name__=='__main__':run()
