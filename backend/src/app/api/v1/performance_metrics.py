import logging
from fastapi import Query
from fastapi.routing import APIRouter

from backend.src.app.api.api_handlers import api_error_handler
from backend.src.app.configs.constants import (
    API_SUCCESS_MESSAGE,
    DataForm,
    PerformanceSection,
    LaneType,
)
from backend.src.app.schemas.performance_metrics import Params, Response
from backend.src.app.services.business_services.performance_metrics import (
    compute_metrics,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/performance", tags=["performance"])


@router.get("/metrics")
@api_error_handler
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
    params = Params(**params)
    data = await compute_metrics(params)
    return {
        "success": True,
        "status_code": 200,
        "message": API_SUCCESS_MESSAGE,
        "data": data,
    }
