"""Synthetic LiveOps offer-price A/B cohort simulator.

IMPORTANT: Assumed behavioral rules and synthetic events, not real players, a
live controlled experiment, or empirical estimates of price elasticity.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
import numpy as np
import pandas as pd

SEGMENTS=("Casual", "Regular", "Enthusiast")
SEGMENT_WEIGHTS=np.array([.50,.35,.15])
PLAY_PROB=np.array([.46,.63,.79])
CHURN_HAZARD=np.array([.048,.032,.022])
EVENT_JOIN=np.array([.55,.70,.84])
OFFER_BASE_PROB=np.array([.014,.026,.048])
ORGANIC_BUY_PROB=np.array([.007,.012,.020])
PRICE_ELASTICITY=np.array([.65,.95,1.20])

@dataclass(frozen=True)
class ExperimentConfig:
    n_users:int=12000
    days:int=21
    event_days:int=14
    seed:int=20261114
    reference_price:float=4.99
    control_price:float=4.99
    treatment_price:float=3.99
    organic_price:float=2.99
    max_daily_milestones:int=2
    completion_milestones:int=8
    def validate(self):
        if self.n_users<100 or self.n_users%2: raise ValueError("n_users must be even and >=100")
        if not 7<=self.event_days<self.days: raise ValueError("Require event_days >=7 and < days")
        if self.control_price<=0 or self.treatment_price<=0 or self.reference_price<=0: raise ValueError("positive prices required")


def simulate(cfg:ExperimentConfig=ExperimentConfig(), collect_events:bool=True):
    """Randomized equal A/B allocation among event-eligible players at event launch.

    All users active on Day 1 by design (event-eligible entry cohort). Only
    limited-time bundle price differs between arms; event content, organic IAP,
    and churn rules are shared. No claim of real-world causal inference.
    """
    cfg.validate()
    n=cfg.n_users; days=cfg.days
    rng=np.random.default_rng(cfg.seed)
    user=np.arange(1,n+1)
    segment_ix=rng.choice(3,size=n,p=SEGMENT_WEIGHTS)
    # Randomization independent of segment, prices and propensity.
    assign=np.array([0]*(n//2)+[1]*(n//2),dtype=np.int8)
    rng.shuffle(assign)
    arm=np.where(assign==0,"Control","Discount")
    price=np.where(assign==0,cfg.control_price,cfg.treatment_price)
    engagement_latent=rng.lognormal(mean=-.06,sigma=.28,size=n)
    spend_latent=rng.lognormal(mean=-.12,sigma=.46,size=n)
    prior_week_sessions=np.minimum(7,rng.poisson(np.array([2.0,3.4,4.7])[segment_ix]))
    alive=np.ones(n,dtype=bool)
    offer_bought=np.zeros(n,dtype=bool)
    organic_purchases=np.zeros(n,dtype=int)
    event_progress=np.zeros(n,dtype=int)
    active_days=np.zeros(n,dtype=int)
    revenue=np.zeros(n,dtype=float)
    offer_revenue=np.zeros(n,dtype=float)
    first_purchase_day=np.zeros(n,dtype=int)
    rows=[]; daily=[]

    def push(mask, day, etype, amount=0.0, milestone=0):
        if not collect_events or not np.any(mask):return
        ids=np.flatnonzero(mask)
        if np.ndim(amount): values=amount[ids]
        else: values=np.full(len(ids),amount,dtype=float)
        if np.ndim(milestone): steps=milestone[ids]
        else: steps=np.full(len(ids),milestone,dtype=int)
        rows.extend(zip(user[ids].tolist(),[day]*len(ids),[etype]*len(ids),values.tolist(),steps.tolist()))

    for day in range(1,days+1):
        active=(alive & (rng.random(n)<np.clip(PLAY_PROB[segment_ix]*engagement_latent,0,.98)))
        if day==1: active[:]=True
        active_days+=active
        push(active,day,"session_start")
        within=day<=cfg.event_days
        join=active & (rng.random(n)<EVENT_JOIN[segment_ix]) if within else np.zeros(n,dtype=bool)
        push(join,day,"event_play")
        # All event content and milestones are the same in Control/Discount.
        extra=(rng.random(n)<np.array([.16,.32,.49])[segment_ix]) & join
        progress_gain=join.astype(int)+extra.astype(int)
        event_progress+=progress_gain
        push(join,day,"milestone_earned",milestone=progress_gain)
        if within:
            # Log exposure before purchase so conversion/exposure denominators are clear.
            exposure=active & (~offer_bought)
            push(exposure,day,"bundle_impression")
            offer_daily=np.clip(OFFER_BASE_PROB[segment_ix]*spend_latent*
                 (cfg.reference_price/price)**PRICE_ELASTICITY[segment_ix],0,.5)
            bought=exposure & (rng.random(n)<offer_daily)
            offer_bought|=bought
            revenue[bought]+=price[bought]
            offer_revenue[bought]+=price[bought]
            first_purchase_day=np.where(bought&(first_purchase_day==0),day,first_purchase_day)
            push(bought,day,"bundle_purchase",amount=price)
        organic=active & (rng.random(n)<np.clip(ORGANIC_BUY_PROB[segment_ix]*spend_latent,0,.45))
        organic_purchases+=organic
        revenue[organic]+=cfg.organic_price
        first_purchase_day=np.where(organic&(first_purchase_day==0),day,first_purchase_day)
        push(organic,day,"organic_purchase",amount=cfg.organic_price)
        # Treatment has no direct effect on player activity/churn in this model.
        churn=alive & (rng.random(n)<CHURN_HAZARD[segment_ix])
        alive[churn]=False
        push(churn,day,"churn")
        daily.append({"day":day,"event_running":int(within),"active_total":int(active.sum()),
              "event_players":int(join.sum()),"bundle_sales":int(np.sum(bought)) if within else 0,
              "organic_sales":int(organic.sum())})

    users=pd.DataFrame({"user_id":user,"variant":arm,"persona":np.array(SEGMENTS)[segment_ix],
            "assigned_price_usd":price,"prior_week_sessions":prior_week_sessions,
            "engagement_latent":engagement_latent,"spend_latent":spend_latent,
            "active_days_21":active_days,"event_milestones":event_progress,
            "event_completed":(event_progress>=cfg.completion_milestones).astype(int),
            "bundle_purchased":offer_bought.astype(int),"organic_purchases":organic_purchases,
            "revenue_usd_21":np.round(revenue,2),"bundle_revenue_usd":np.round(offer_revenue,2),
            "first_purchase_day":first_purchase_day})
    if collect_events:
        ev=pd.DataFrame(rows,columns=["user_id","day","event_type","revenue_usd","milestones"])
        ev=ev.merge(users[["user_id","variant","persona"]],on="user_id",how="left",validate="many_to_one")
        ev.insert(0,"event_id",np.arange(1,len(ev)+1))
        ev=ev[["event_id","user_id","variant","persona","day","event_type","revenue_usd","milestones"]]
        ev["revenue_usd"]=ev["revenue_usd"].round(2)
    else: ev=pd.DataFrame(columns=["event_id","user_id","variant","persona","day","event_type","revenue_usd","milestones"])
    return users,ev,pd.DataFrame(daily)


def summarize(users:pd.DataFrame, events:pd.DataFrame, cfg:ExperimentConfig):
    e14=events[events.day<=cfg.event_days]
    active=e14[e14.event_type=="session_start"].groupby(["variant","day"]).user_id.nunique()
    rev=e14[e14.revenue_usd>0].groupby(["variant","day"]).revenue_usd.sum()
    dau=active.rename("dau").reset_index()
    dau["revenue_usd"]=dau.apply(lambda r:float(rev.get((r.variant,r.day),0)),axis=1)
    dau["arpdau_usd"]=dau.revenue_usd/dau.dau
    rows=[]
    for variant,group in users.groupby("variant"):
        ids=set(group.user_id)
        block=e14[e14.user_id.isin(ids)]
        payers=block.loc[block.revenue_usd>0,"user_id"].nunique()
        event_rev=float(block.revenue_usd.sum())
        offer_rev=float(block.loc[block.event_type=="bundle_purchase","revenue_usd"].sum())
        active_d7=block.loc[(block.day==7)&(block.event_type=="session_start"),"user_id"].nunique()
        active_d14=block.loc[(block.day==14)&(block.event_type=="session_start"),"user_id"].nunique()
        rows.append({"variant":variant,"assigned_users":len(group),"price_usd":group.assigned_price_usd.iloc[0],
           "iap_revenue_usd_d14":round(event_rev,2),"iap_rpu_usd_d14":event_rev/len(group),
           "iap_arppu_usd_d14":event_rev/payers if payers else 0,
           "payer_conversion_d14":payers/len(group),
           "bundle_conversion_d14":group.bundle_purchased.mean(),
           "bundle_revenue_usd_d14":round(offer_rev,2),
           "d7_return":active_d7/len(group),"d14_return":active_d14/len(group),
           "event_completion_rate_d21":group.event_completed.mean(),
           "revenue_usd_d21":float(group.revenue_usd_21.sum())})
    return pd.DataFrame(rows).sort_values("variant").reset_index(drop=True),dau


def segment_summary(users:pd.DataFrame, events:pd.DataFrame, event_days:int):
    s=events[(events.day<=event_days) & (events.revenue_usd>0)].groupby(["variant","persona"]).revenue_usd.sum()
    rows=[]
    for (arm,persona),g in users.groupby(["variant","persona"]):
        e=events[(events.variant==arm)&(events.persona==persona)&(events.day<=event_days)]
        payers=e.loc[e.revenue_usd>0,"user_id"].nunique()
        rows.append({"variant":arm,"persona":persona,"assigned":len(g),
           "payer_conversion":payers/len(g),"bundle_conversion":g.bundle_purchased.mean(),
           "iap_rpu_d14":float(s.get((arm,persona),0))/len(g),
           "event_completion_rate":g.event_completed.mean(),
           "d7_return":e.loc[(e.day==7)&(e.event_type=="session_start"),"user_id"].nunique()/len(g)})
    return pd.DataFrame(rows)
