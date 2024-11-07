import logging
from os import getenv
import pandas as pd
from backend.src.app.clients.storage.azure_blob import BlobClientHandler
from backend.src.app.configs.constants import CONFIGS
from backend.src.app.services.data_reader import (
    read_csv,
    read_historical_data_from_cloud,
)


logger = logging.getLogger(__name__)


def initialize_historical_data() -> None:
    if "HISTORICAL_DATA_FRAME" in CONFIGS and isinstance(
        CONFIGS["HISTORICAL_DATA_FRAME"], pd.DataFrame
    ):
        logger.info("Historical data set already initialized")
        return
    CONFIGS["HISTORICAL_DATA_FRAME"] = read_csv(getenv("HISTORICAL_DATA_PATH"))
    logger.info("Historical data set successfully")
    return


async def initialize_historical_data_from_cloud() -> None:
    if "HISTORICAL_DATA_FRAME" in CONFIGS and isinstance(
        CONFIGS["HISTORICAL_DATA_FRAME"], pd.DataFrame
    ):
        logger.info("Historical data set already initialized")
        return
    client = BlobClientHandler()
    df = await read_historical_data_from_cloud(client)
    if isinstance(df, pd.DataFrame) and not df.empty:
        CONFIGS["HISTORICAL_DATA_FRAME"] = df
        logger.info("Historical data set successfully")
        return
    logger.error("Failed to initialize historical data set")
    return
