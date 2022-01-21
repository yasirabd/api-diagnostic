import numpy as np
from typing import List
import os

from fastapi import APIRouter, Depends, Query, Body
from api_v1.estimate.vbm import VBM
from api_v1.residual.residual import Residual


router = APIRouter()

@router.get("/estimates")
async def estimate_sensor(sensors: List[str] =  Query(['Generator Gross Capacity', 'Turbine Lube Oil Cooler Outlet Temperature', 'Turbine Bearing #01 Metal Temperature', 'Turbine.Bearing 1 Metal Temperature', 'Turbine.Bearing Oil Pressure', 'Turbine.Bearing 1 Drain Oil Temperature']),
                          actuals: List[float] = Query([594.6552, 46.3567619, 79.52576, 84.71144, 1.288945, 51.4658165]), 
                          date: str = 'date', state_matrix: str = 'path'):
    # load state matrix
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'state_matrix.npy')
    state_matrix = np.load(path)
    
    # calculate reference data
    actual_low = [433.969025, 41.625633, 75.298727, 80.187670, 1.467023, 47.407933]
    actual_high = [610.248900, 47.335740, 92.167030, 87.590470, 1.512295, 56.443672]
    vbm = VBM(actual_low, actual_high)
    estimates, state_matrix = vbm.estimate_sensors(actuals, state_matrix)

    # calculate residual values
    residual_negative_treshold = [-177, -6, -16, -7.180405, -0.06, -8]
    residual_positive_treshold = [177, 6, 16, 7.180405, 0.06, 8]

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