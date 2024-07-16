# external packages and objects
import os
import datetime as dt
from fastapi import APIRouter, Depends, Response, Path, Body
from schemas.params import Params
from surquest.utils.loader import Loader
from surquest.fastapi.schemas.responses import (
    Response,
    Responses,
    Message
)

# internal packages and objects
from settings import formatter, FX, Endpoints
from enums.currencies import currencies

router = APIRouter()


@router.get(
    Endpoints.get("ETL.subjects"),
    name="Get Subjects (Currency Pairs)",
    tags=["ETL"],
    operation_id="get_subjects",
    responses=Responses.get(),
    response_model_exclude_none=True,
)
def get_subjects():
    """Method returns list of subjects (currencies) available for ETL."""

    return Response.set(
        data=currencies
    )

@router.get(
    Endpoints.get("ETL.config"),
    name="Get ETL config",
    tags=["ETL"],
    operation_id="get_config",
    responses=Responses.get(),
    response_model_exclude_none=True,
)
def get_config(
        currency: Params.currency().type_ = Params.currency().query
):
    fx = FX.get(currency=currency.value)

    today = dt.datetime.today().strftime("%Y-%m-%d")
    now = dt.datetime.now().strftime("%H%M%S")

    journal_table_conf = Loader.load_yaml(
        path=F"{os.getenv('HOME')}/config/subjects/fx.BQ-table.yaml"
    )

    return Response.set(
        data={
            "ETL": {
                "currency": fx
            },
            "BQ": {
                "dataset": formatter.get("bigquery.datasets.raw"),
                "tables": {
                    "destination": {
                        "name": journal_table_conf.get("name"),
                        "config": journal_table_conf
                    }
                }
            },
            "GCS": {
                "bucket": formatter.get("storage.buckets.ingress").lower(),
                "blobs": {
                    "merged": F"{today}/{now}/{currency.value.upper()}/merged.jsonl",
                },
                "prefixes": {
                    "raw": F"{today}/{now}/{currency.value.upper()}/raw",
                    "bq": F"{today}/{now}/{currency.value.upper()}/bq",
                    "tmp": F"{today}/{now}/{currency.value.upper()}/tmp",
                }
            }
        }
    )
