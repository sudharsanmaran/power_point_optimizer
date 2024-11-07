from abc import ABC, abstractmethod


# Abstract base class
class StorageClient(ABC):
    @abstractmethod
    async def initialize_client(self, *args, **kwargs):
        """
        Initializes the storage client.
        """
        pass

    @abstractmethod
    async def read_historical_data(self, *args, **kwargs):
        """
        Reads data from the storage and returns it as a DataFrame.
        """
        pass
