from os import getenv
from azure.storage.blob.aio import BlobServiceClient
import pandas as pd
from io import StringIO

from backend.src.app.clients.storage.base import StorageClient


class BlobClientHandler(StorageClient):
    def __init__(self):
        """
        Initializes the BlobClientHandler with Azure Blob
        connection parameters.
        """
        self.connection_string = getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = getenv("AZURE_STORAGE_CONTAINER_NAME")
        self.blob_name = getenv("AZURE_STORAGE_BLOB_NAME")
        self.blob_client = None

    async def initialize_client(self):
        """
        Initializes the Azure Blob client.
        """
        try:
            blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            self.blob_client = blob_service_client.get_blob_client(
                container=self.container_name, blob=self.blob_name
            )
        except Exception as e:
            print(f"Error initializing Azure Blob client: {e}")
            self.blob_client = None

    async def read_historical_data(self):
        """
        Reads data from Azure Blob Storage asynchronously
        and returns it as a DataFrame.
        """
        if not self.blob_client:
            print("Blob client is not initialized.")
            return None

        try:
            # Download blob content asynchronously
            stream = await self.blob_client.download_blob()
            file_content = await stream.readall()

            # todo: find out if we need to close the blob client
            # await self.blob_client.close()

            # Convert content to DataFrame
            df = pd.read_csv(StringIO(file_content.decode("utf-8")))
            return df
        except Exception as e:
            print(f"Error reading historical data from Azure: {e}")
            return None
