from functools import wraps
import logging

from fastapi import HTTPException
from pydantic import ValidationError

from backend.src.app.services.business_services.errors import EmptyDataError


logger = logging.getLogger(__name__)


def api_error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        # todo: db error handling
        except EmptyDataError as e:
            logger.error(f"Error processing request: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except ValidationError as e:
            logger.error(f"Error validating request: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        # todo: uncomment in production
        # except Exception as e:
        #     logger.error(f"Unexpected error: {e}")
        #     raise HTTPException(status_code=500, detail=str(e))

    return wrapper
