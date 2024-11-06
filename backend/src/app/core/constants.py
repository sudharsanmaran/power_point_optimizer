from enum import Enum
import logging
from os import getenv

import pandas as pd

from backend.src.app.services.data_reader import read_csv


logger = logging.getLogger(__name__)

CONFIGS = {}
API_SUCCESS_MESSAGE = "success"


class DataForm(Enum):
    REMODEL = "remodel"
    HISTORICAL = "historical"
    SAVED_MODEL = "saved_model"


class PerformanceSection(Enum):
    WAIT_TIME = "wait_time"


class LaneType(Enum):
    MANNED_TRADITIONAL = "Manned Traditional"
    REVERSIBLE_MCO_TRADITIONAL_EXPRESS = "Reversible MCO Traditional Express"
    SCO_BULLPEN = "SCO Bullpen"
    MANNED_EXPRESS = "Manned Express"
    SCO_INDIVIDUAL = "SCO Individual"


def initialize_historical_data() -> None:
    global CONFIGS
    if "HISTORICAL_DATA_FRAME" in CONFIGS and isinstance(
        CONFIGS["HISTORICAL_DATA_FRAME"], pd.DataFrame
    ):
        logger.info("Historical data set already initialized")
        return
    CONFIGS["HISTORICAL_DATA_FRAME"] = read_csv(getenv("HISTORICAL_DATA_PATH"))
    logger.info("Historical data set successfully")
    return
