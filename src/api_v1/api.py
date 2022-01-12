import numpy as np

from fastapi import APIRouter, Depends
from api_v1.estimate.vbm import VBM


router = APIRouter()

@router.get("/estimate/")
async def estimate_sensor(actual: list, date: str, state_matrix: str):
    # load state matrix
    state_m = np.load('src/state_matrix.npy')
    actual = np.array([594.6552, 46.3567619, 79.52576, 84.71144, 1.288945, 51.4658165])

    vbm = VBM()
    dynamic_m, weight = vbm.create_dynamic_matrix(state_m, actual)
    estimate = vbm.estimate_value(dynamic_m, weight)
    print(estimate)

    return {"message": "success"}