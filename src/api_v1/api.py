import numpy as np
from typing import List
import os

from fastapi import APIRouter, Depends, Query, Body
from api_v1.estimate.vbm import VBM


router = APIRouter()

@router.get("/estimates")
async def estimate_sensor(actual: float = 10., date: str = 'date', state_matrix: str = 'path'):
    # load state matrix
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'state_matrix.npy')
    state_m = np.load(path)
    actuals = np.array([594.6552, 46.3567619, 79.52576, 84.71144, 1.288945, 51.4658165])

    vbm = VBM()
    dynamic_m, weight = vbm.create_dynamic_matrix(state_m, actuals)
    estimate = vbm.estimate_value(dynamic_m, weight)

    return {"message": "success", "estimate": list(estimate)}