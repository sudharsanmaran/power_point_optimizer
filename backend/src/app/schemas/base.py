from typing import Any, Optional
from pydantic import BaseModel


class CommonResponse(BaseModel):
    status_code: int
    success: bool
    message: str
    data: Optional[Any] = None
