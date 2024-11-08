# Standard Library Imports
import logging
from contextlib import asynccontextmanager

# Third-Party Imports
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse


# from Secweb import SecWeb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# flake8: noqa
# Local Application Imports
from backend.src.app.errors import ImproperlyConfigured
from backend.src.app.configs.startup import (
    initialize_historical_data_from_cloud,
    load_environment_variables,
)
from backend.src.app.schemas.base import CommonResponse
from backend.src.app.api.v1.performance_metrics import router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code
    load_environment_variables()
    await initialize_historical_data_from_cloud()
    # 3. establish database connection
    # 4. load basic data into database (create/update)
    yield
    # teardown code
    # 1. clear model data
    # 2. clear history df to free up space


app = FastAPI(
    title="Power Point Optimizer", version="2.0.0", lifespan=lifespan
)


@app.middleware("http")
async def set_permissions_policy_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Permissions-Policy"] = ""
    return response


# SecWeb(
#     app=app,
#     Option={
#         "hsts": {"max-age": 2592000},
#         "csp": {
#             "object-src": ["'none'"],
#             "style-src": ["'self'", "'unsafe-inline'"],
#             "script-src": ["'self'", "'unsafe-inline'"],
#             "base-uri": ["'self'"],
#         },
#     },
# )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc) -> JSONResponse:
    if exc.status_code == 500:
        message = "Internal Server Error"
    else:
        message = exc.detail
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": message,
        },
    )


app.add_middleware(GZipMiddleware)

app.include_router(router)


@app.get("/")
async def root() -> CommonResponse:
    return {
        "status_code": 200,
        "success": True,
        "message": "application started successfully",
    }
