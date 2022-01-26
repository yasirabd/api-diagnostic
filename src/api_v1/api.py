from functools import lru_cache
from typing import List

from fastapi import APIRouter, Depends, Query, Body
from api_v1.estimate.vbm import VBM
from api_v1.residual.residual import Residual
from api_v1.utils.s3_utils import S3
import config


router = APIRouter()

@lru_cache()
def get_settings():
    return config.Settings()

@router.get("/estimates")
async def estimate_sensor(date: str = 'date', sensors: List[str] = Query(None), actuals: List[float] = Query(None),
                          settings: config.Settings = Depends(get_settings)):

    # load state matrix from s3
    s3 = S3(date=date, 
            bucket_name=settings.AWS_S3_BUCKET_NAME,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION)
    if s3.check_if_file_exists():
        state_matrix = s3.load_state_matrix()
    else:
        # load the previous state matrix
        state_matrix = s3.load_previous_state_matrix()
    
    # calculate reference data
    actual_low = [433., 41., 80., 1.48, 47.]
    actual_high = [610., 47., 87.18045, 1.54, 55.]
    vbm = VBM(actual_low, actual_high)
    estimates, state_matrix = vbm.estimate_sensors(actuals, state_matrix)

    # update state matrix in s3
    s3.upload_state_matrix(state_matrix)

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