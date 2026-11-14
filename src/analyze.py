"""Descriptive metrics and player-level uncertainty for synthetic A/B assignment."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats

METRICS=("iap_rpu_d14","payer_d14","bundle_purchased","d7_return","event_completion")

def user_metrics(users:pd.DataFrame,events:pd.DataFrame,event_days:int=14):
    # One row per randomized user: correct unit of analysis for the experiment.
    e=events[events.day<=event_days]
    rev=e.groupby("user_id").revenue_usd.sum()
    payer=e[e.revenue_usd>0].groupby("user_id").size()
    d7=e[(e.day==7)&(e.event_type=="session_start")].groupby("user_id").size()
    x=users[["user_id","variant","persona","bundle_purchased","event_completed","prior_week_sessions"]].copy()
    x["iap_rpu_d14"]=x.user_id.map(rev).fillna(0)
    x["payer_d14"]=x.user_id.isin(payer.index).astype(int)
    x["d7_return"]=x.user_id.isin(d7.index).astype(int)
    x["event_completion"]=x.event_completed.astype(int)
    return x


def compare_groups(x:pd.DataFrame,bootstrap:int=1000,seed:int=8471):
    """Independent randomized cohorts; bootstrap users, not daily metric rows.

    CI is sampling uncertainty IN THE SIMULATOR, not market evidence.
    """
    rng=np.random.default_rng(seed)
    a=x[x.variant=="Control"]; b=x[x.variant=="Discount"]
    rows=[]
    for metric in METRICS:
        arr_a=a[metric].to_numpy(float);arr_b=b[metric].to_numpy(float)
        d=arr_b.mean()-arr_a.mean()
        bs_a=arr_a[rng.integers(0,len(arr_a),(bootstrap,len(arr_a)))].mean(axis=1)
        bs_b=arr_b[rng.integers(0,len(arr_b),(bootstrap,len(arr_b)))].mean(axis=1)
        diffs=bs_b-bs_a
        ci=np.percentile(diffs,[2.5,97.5])
        # Welch's t uses independent user observations, not repeated-day pseudoreplication.
        p=float(stats.ttest_ind(arr_b,arr_a,equal_var=False).pvalue)
        rows.append({"metric":metric,"control":arr_a.mean(),"discount":arr_b.mean(),
           "delta_discount_minus_control":d,"ci_lower_95":ci[0],"ci_upper_95":ci[1],
           "welch_p_synthetic":p,"n_control":len(a),"n_discount":len(b)})
    return pd.DataFrame(rows)


def decision(comparison:pd.DataFrame):
    c=comparison.set_index("metric")
    primary=c.loc["iap_rpu_d14"]
    d7=c.loc["d7_return"]
    comp=c.loc["event_completion"]
    gates={"primary_revenue_lower_ci_positive":bool(primary.ci_lower_95>0),
      "d7_guardrail_lower_ci_at_least_minus_1_5pp":bool(d7.ci_lower_95>=-.015),
      "event_completion_lower_ci_at_least_minus_2pp":bool(comp.ci_lower_95>=-.02)}
    return {"decision":"SIMULATED GO" if all(gates.values()) else "SIMULATED HOLD",
       "gates":gates,"interpretation":"Training exercise only. Never deploy from synthetic evidence."}
