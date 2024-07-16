"""This is the main entry point for the ETL application defined with FastAPI."""
import os
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from fastapi import FastAPI, Request, Query

# import local packages and objects
from settings import formatter
from routes.BQ import bigquery
from routes.GCS import storage
from routes.config import config
from routes.data import data
from surquest.fastapi.utils.route import Route
from surquest.fastapi.utils.GCP.middleware import LoggingMiddleware
from surquest.fastapi.utils.GCP.catcher import (
    catch_validation_exceptions,
    catch_http_exceptions,
)

PATH_PREFIX = os.getenv('PATH_PREFIX','')

app = FastAPI(
    title=F"{formatter.config.get('solution').get('code').upper()} FX ETL",
    description=F"""Service supporting the ormatter.config.get('solution').get('code').upper() ETL process sourcing data 
    related to exchange rates into Google Cloud Storage and BigQuery.
    """,
    openapi_url=F"{PATH_PREFIX}/openapi.json",
    version=os.getenv('SERVICE_VERSION', 'undefined')
)

# add middleware
app.add_middleware(LoggingMiddleware)

# exception handlers
app.add_exception_handler(HTTPException, catch_http_exceptions)
app.add_exception_handler(RequestValidationError, catch_validation_exceptions)

# custom routes to documentation and favicon
app.add_api_route(path=F"{PATH_PREFIX}/", endpoint=Route.get_documentation, include_in_schema=False)
app.add_api_route(path=PATH_PREFIX, endpoint=Route.get_favicon, include_in_schema=False)

# add routers
app.include_router(storage.router, prefix=PATH_PREFIX)
app.include_router(bigquery.router, prefix=PATH_PREFIX)
app.include_router(config.router, prefix=PATH_PREFIX)
app.include_router(data.router, prefix=PATH_PREFIX)

