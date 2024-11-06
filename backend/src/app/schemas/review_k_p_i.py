import logging
from typing import Dict, List, Union

from pydantic import BaseModel, field_validator
from backend.src.app.core.constants import (
    DataForm,
    LaneType,
    PerformanceSection,
)
from backend.src.app.schemas.base import CommonResponse


logger = logging.getLogger(__name__)


class Params(BaseModel):
    type: PerformanceSection = PerformanceSection.WAIT_TIME
    cluster: int = 1
    store: List[int] = [
        16,
        29,
        45,
        49,
        60,
        63,
        121,
        171,
        180,
        201,
        305,
        306,
        338,
    ]
    peak_hour: List[int] = [0, 1]
    lane_types: List[LaneType] = [lane_type for lane_type in LaneType]
    data_form: DataForm = DataForm.HISTORICAL
    covid_flag: bool = False
    october_flag: bool = False
    events_flag: bool = False
    total_year_flag: bool = False
    time_period: int = 0

    @field_validator("cluster", mode="after")
    def validate_cluster(cls, v):
        if v < 1 or v > 4:
            logger.error("Cluster should be between 1 and 4")
            raise ValueError("cluster should be between 1 and 4")
        return v


class DFSplitFormat(BaseModel):
    index: List[
        Union[int, str]
    ]  # index can be integers or strings depending on DataFrame
    columns: List[str]  # column names as strings
    data: List[List[Union[str, int, float]]]  # each row with mixed data types


class Response(CommonResponse):
    data: Dict[str, DFSplitFormat]
