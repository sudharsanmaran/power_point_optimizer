import logging
from fastapi import Query, HTTPException
from fastapi.routing import APIRouter
from pydantic import ValidationError

from backend.src.app.core.constants import (
    API_SUCCESS_MESSAGE,
    DataForm,
    PerformanceSection,
    LaneType,
)
from backend.src.app.schemas.review_k_p_i import Params, Response
from backend.src.app.services.review_k_p_i import process_review_k_p_i


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("/reviewkpi")
async def get_review_kpi(
    type: PerformanceSection = Query(
        PerformanceSection.WAIT_TIME, description="Type of KPI"
    ),
    cluster: int = Query(default=1, description="Cluster name", ge=1, le=4),
    store: list[int] = Query(
        default=[16, 29, 45, 49, 60, 63, 121, 171, 180, 201, 305, 306, 338],
        description="List of store numbers",
    ),
    peak_hour: list[int] = Query(
        default=[0, 1], description="List of peak hours"
    ),
    lane_types: list[LaneType] = Query(
        [lane_type for lane_type in LaneType], description="List of lane types"
    ),
    data_form: DataForm = DataForm.HISTORICAL,
    covid_flag: bool = False,
    october_flag: bool = False,
    events_flag: bool = False,
    total_year_flag: bool = False,
    time_period: int = 0,
) -> Response:
    params = {
        "type": type,
        "data_form": data_form,
        "cluster": cluster,
        "store": store,
        "peak_hour": peak_hour,
        "lane_types": lane_types,
        "covid_flag": covid_flag,
        "october_flag": october_flag,
        "events_flag": events_flag,
        "total_year_flag": total_year_flag,
        "time_period": time_period,
    }
    try:
        params = Params(**params)
        data = await process_review_k_p_i(params)
        return {
            "success": True,
            "status_code": 200,
            "message": API_SUCCESS_MESSAGE,
            "data": data,
        }

    except ValueError as e:
        logger.error(f"Error processing review KPI: {e}")
        raise HTTPException(status_code=404, detail=str(e))

    except ValidationError as e:
        logger.error(f"Error validating review KPI params: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error processing review KPI: {e}")
        raise HTTPException(status_code=500, detail=str(e))
