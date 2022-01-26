import numpy as np
from typing import List
import os

from fastapi import APIRouter, Depends, Query, Body
from api_v1.estimate.vbm import VBM
from api_v1.residual.residual import Residual


router = APIRouter()

@router.get("/estimates")
async def estimate_sensor(date: str = 'date', sensors: List[str] = Query(None), actuals: List[float] = Query(None)):
    # load state matrix
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data6_state_matrix.npy')
    state_matrix = np.load(path)
    
    # calculate reference data
    actual_low = [433., 41., 80., 1.48, 47.]
    actual_high = [610., 47., 87.18045, 1.54, 55.]
    vbm = VBM(actual_low, actual_high)
    estimates, state_matrix = vbm.estimate_sensors(actuals, state_matrix)

    # calculate residual values
    residual_negative_treshold = [-177, -6, -7.180405, -0.06, -8]
    residual_positive_treshold = [177, 6, 7.180405, 0.06, 8]

    residual_indication_positives = []
    residual_indication_negatives = []
    residuals = []
    for i in range(len(actuals)):
        resid = Residual(actuals[i], estimates[i], residual_positive_treshold[i], residual_negative_treshold[i])
        residuals.append(resid.residual)
        residual_indication_positives.append(resid.residual_indication_positive)
        residual_indication_negatives.append(resid.residual_indication_negative)

    return {"sensors": sensors, "actuals": actuals, "estimates": list(estimates), "residuals": residuals, 
            "residual_indication_positive": residual_indication_positives, "residual_indication_negative": residual_indication_negatives,
            "state_matrix": state_matrix.shape}