from enum import Enum
import logging


logger = logging.getLogger(__name__)

CONFIGS = {}
API_SUCCESS_MESSAGE = "success"
EVENTS = [
    "Halloween",
    "Thanksgiving",
    "Christmas",
    "New Year",
    "Valentine's Day",
]


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
