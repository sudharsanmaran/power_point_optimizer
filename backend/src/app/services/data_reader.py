# import aiofiles
from io import StringIO
import pandas as pd
from azure.storage.blob.aio import BlobServiceClient
import logging

logger = logging.getLogger(__name__)


def read_csv(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        logger.info(f"successfully read  data from {path}")
        return df

    except Exception as e:
        logger.error(f"Error reading data from {path}: {e}")
        return pd.DataFrame()


async def read_historical_data_from_azure():
    try:
        # Initialize the Azure Blob client
        blob_service_client = BlobServiceClient.from_connection_string(
            "your_connection_string"
        )
        blob_client = blob_service_client.get_blob_client(
            container="your_container_name", blob="historical_data.csv"
        )

        # Download blob content asynchronously
        stream = await blob_client.download_blob()
        file_content = await stream.readall()

        # Convert content to DataFrame
        df = pd.read_csv(StringIO(file_content.decode("utf-8")))
        return df

    except Exception as e:
        print(f"Error reading historical data from Azure: {e}")
        return None
