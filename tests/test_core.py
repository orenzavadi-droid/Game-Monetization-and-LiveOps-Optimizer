from dataclasses import replace
import numpy as np
import pytest
from src.model import ExperimentConfig,simulate,summarize,segment_summary
from src.analyze import user_metrics,compare_groups,decision
from src.pricing import pricing_sensitivity

@pytest.fixture(scope='module')
def sample():
    c=ExperimentConfig(n_users=400,days=21,seed=33)
    return c,*simulate(c)

def test_even_cohort_required():
    with pytest.raises(ValueError):simulate(ExperimentConfig(n_users=101))
def test_positive_prices_required():
    with pytest.raises(ValueError):simulate(ExperimentConfig(treatment_price=0))
def test_cohort_randomization(sample):
    c,u,e,d=sample
    assert u.variant.value_counts().to_dict()=={'Control':200,'Discount':200}
def test_user_key_unique(sample):
    c,u,e,d=sample
    assert u.user_id.is_unique
    assert e.event_id.is_unique
def test_immutable_assignments_in_event_log(sample):
    c,u,e,d=sample
    lookup=u.set_index('user_id').variant
    assert (e.variant==e.user_id.map(lookup)).all()
def test_first_day_all_users_active(sample):
    c,u,e,d=sample
    assert e[(e.day==1)&(e.event_type=='session_start')].user_id.nunique()==400
def test_organic_price_same_between_groups(sample):
    c,u,e,d=sample
    o=e[e.event_type=='organic_purchase']
    assert o.empty or set(o.revenue_usd)=={c.organic_price}
def test_offer_price_only_arm_difference(sample):
    c,u,e,d=sample
    purchases=e[e.event_type=='bundle_purchase']
    assert purchases.empty or all(np.isclose(purchases.revenue_usd, purchases.variant.map({'Control':c.control_price,'Discount':c.treatment_price})))
def test_no_offer_purchase_after_event(sample):
    c,u,e,d=sample
    assert e[e.event_type=='bundle_purchase'].day.max()<=c.event_days
def test_offer_once(sample):
    c,u,e,d=sample
    assert e[e.event_type=='bundle_purchase'].user_id.value_counts().max()<=1
def test_nonnegative_income(sample):
    c,u,e,d=sample
    assert (u.revenue_usd_21>=0).all()
def test_revenue_ledger(sample):
    c,u,e,d=sample
    ledger=e.groupby('user_id').revenue_usd.sum()
    assert np.allclose(u.revenue_usd_21,u.user_id.map(ledger).fillna(0))
def test_all_payments_logged(sample):
    c,u,e,d=sample
    assert np.isclose(u.revenue_usd_21.sum(),e.revenue_usd.sum())
def test_event_progress_log(sample):
    c,u,e,d=sample
    prog=e.groupby('user_id').milestones.sum()
    assert (u.event_milestones==u.user_id.map(prog).fillna(0)).all()
def test_primary_denominator(sample):
    c,u,e,d=sample
    a,_=summarize(u,e,c)
    for _,r in a.iterrows():
        total=e[(e.variant==r.variant)&(e.day<=c.event_days)].revenue_usd.sum()
        assert np.isclose(r.iap_rpu_usd_d14,total/r.assigned_users)
def test_retention_bounds(sample):
    c,u,e,d=sample
    a,_=summarize(u,e,c)
    assert a.d7_return.between(0,1).all()
def test_segment_invariance(sample):
    c,u,e,d=sample
    seg=segment_summary(u,e,c.event_days)
    assert seg.assigned.sum()==400
def test_user_level_uncertainty(sample):
    c,u,e,d=sample
    ux=user_metrics(u,e,c.event_days)
    assert len(ux)==400
    comp=compare_groups(ux,bootstrap=60)
    assert len(comp)==5
    assert comp.ci_lower_95.notna().all()
def test_decision_is_guardrailed(sample):
    c,u,e,d=sample
    comp=compare_groups(user_metrics(u,e,c.event_days),bootstrap=60)
    ans=decision(comp)
    assert ans['decision'] in ('SIMULATED HOLD','SIMULATED GO')
    assert len(ans['gates'])==3
def test_price_sensitivity_grid(sample):
    c,u,e,d=sample
    s=pricing_sensitivity(u,e,event_days=c.event_days)
    assert len(s)==18
    assert s.expected_bundle_conversion.between(0,1).all()
def test_seed_reproducibility():
    c=ExperimentConfig(n_users=200,seed=123)
    a=simulate(c,collect_events=False)[0]
    b=simulate(c,collect_events=False)[0]
    assert a.equals(b)
def test_different_seeds_change_outcomes():
    c=ExperimentConfig(n_users=200)
    a=simulate(replace(c,seed=1),False)[0]
    b=simulate(replace(c,seed=2),False)[0]
    assert not a.equals(b)
def test_price_change_does_not_change_activity_under_model():
    c=ExperimentConfig(n_users=200,seed=81)
    u1,e1,_=simulate(c)
    u2,e2,_=simulate(replace(c,treatment_price=2.99))
    a=e1[e1.event_type=='session_start'][['user_id','day']].reset_index(drop=True)
    b=e2[e2.event_type=='session_start'][['user_id','day']].reset_index(drop=True)
    # same draw stream usage each day and event purchase; no branch-specific RNG calls
    assert a.equals(b)
