import pandas as pd
import logging

from backend.src.app.clients.storage.base import StorageClient

logger = logging.getLogger(__name__)


def read_csv(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        logger.info(f"successfully read  data from {path}")
        return df

    except Exception as e:
        logger.error(f"Error reading data from {path}: {e}")
        return pd.DataFrame()


async def read_historical_data_from_cloud(
    client: StorageClient,
) -> pd.DataFrame:
    # Initialize the client
    await client.initialize_client()

    # Read data
    df = await client.read_historical_data()
    return df
