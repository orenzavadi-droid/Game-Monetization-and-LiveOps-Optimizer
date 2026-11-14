"""Exploratory price sensitivity. Hypothesis-driven, NOT learned elasticity."""
import numpy as np
import pandas as pd
from src.model import SEGMENTS,OFFER_BASE_PROB,PRICE_ELASTICITY


def pricing_sensitivity(users:pd.DataFrame,events:pd.DataFrame,reference:float=4.99,event_days:int=14):
    # Number of modelled offer opportunities before purchase is NOT a counterfactual
    # exposure count; use all active event days as a common fixed opportunity proxy.
    active=events[(events.day<=event_days)&(events.event_type=="session_start")].groupby("user_id").size()
    exposures=users.user_id.map(active).fillna(0).to_numpy(int)
    ix=users.persona.map({s:i for i,s in enumerate(SEGMENTS)}).to_numpy(int)
    latent=users.spend_latent.to_numpy(float)
    rows=[]
    for scale_name,scale in [("Low sensitivity",.65),("Base assumptions",1.0),("High sensitivity",1.50)]:
        for price in [3.49,3.99,4.49,4.99,5.49,5.99]:
            daily=np.clip(OFFER_BASE_PROB[ix]*latent*(reference/price)**(PRICE_ELASTICITY[ix]*scale),0,.5)
            probability=1-(1-daily)**exposures
            rows.append({"assumption":scale_name,"offer_price_usd":price,
               "expected_bundle_conversion":float(probability.mean()),
               "expected_bundle_rpu_usd":float(price*probability.mean()),
               "base_users":len(users)})
    return pd.DataFrame(rows)
