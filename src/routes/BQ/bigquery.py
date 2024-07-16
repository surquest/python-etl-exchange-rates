# external packages and objects
from fastapi import APIRouter, Body, Query
from surquest.fastapi.utils.GCP.tracer import Tracer
from surquest.fastapi.utils.GCP.logging import Logger
from surquest.GCP.bq.grid import Grid
from surquest.fastapi.schemas.responses import (
    Response,
    Responses,
    Message
)

from .params import BQParams
from settings import Endpoints

router = APIRouter()


@router.get(
    Endpoints.get("BQ.dataset.table.exist"),
    name="Check if exists",
    tags=["BigQuery"],
    operation_id="exist_bq_table",
    responses=Responses.get(),
    response_model_exclude_none=True
)
def exist_bq_table(
        dataset: BQParams.dataset().type_ = BQParams.dataset().path,
        table: BQParams.table().type_ = BQParams.table().path,
):
    grid = Grid(
        name=table,
        dataset=dataset
    )

    return Response.set(
        data={
            "exist": grid.exist(),
            "ref": grid.table_ref._properties
        }
    )


@router.post(
    Endpoints.get("BQ.dataset.table.create"),
    name="Create table",
    tags=["BigQuery"],
    operation_id="create_bq_table",
    responses=Responses.get(),
    response_model_exclude_none=True
)
def create_bq_table(
        dataset: BQParams.dataset().type_ = BQParams.dataset().path,
        table: BQParams.table().type_ = BQParams.table().path,
        config: dict = Body(...),
):
    # get configuration of exchange rate table
    with Tracer.start_span("Create BQ table"):
        config["name"] = table

        grid = Grid.from_dict(
            config=config,
            dataset=dataset
        )

        grid.create()

    return Response.set(
        status_code=201,
        data={
            "exist": grid.exist(),
            "ref": grid.table_ref._properties
        }
    )


@router.patch(
    Endpoints.get("BQ.dataset.table.truncate"),
    name="Truncate BQ table",
    tags=["BigQuery"],
    operation_id="truncate_bq_table",
    responses=Responses.get(),
    response_model_exclude_none=True
)
def truncate_bq_table(
        dataset: BQParams.dataset().type_ = BQParams.dataset().path,
        table: BQParams.table().type_ = BQParams.table().path,
):
    grid = Grid(
        name=table,
        dataset=dataset
    )

    exist = grid.exist()

    if exist is False:
        return Response.set(
            warnings=[
                Message(
                    msg=f"Table {table} does not exist in dataset {dataset}",
                    type="NOT_FOUND",
                    loc=["path", "dataset", "table"],
                    ctx={
                        "table": table,
                        "dataset": dataset,
                    }
                )
            ]
        )

    if exist is True:
        grid.truncate()

        return Response.set()


@router.delete(
    Endpoints.get("BQ.dataset.table.drop"),
    name="Drop BQ table",
    tags=["BigQuery"],
    operation_id="drop_bq_table",
    response_model_exclude_none=True
)
def drop_bq_table(
        dataset: BQParams.dataset().type_ = BQParams.dataset().path,
        table: BQParams.table().type_ = BQParams.table().path,
):
    grid = Grid(
        name=table,
        dataset=dataset
    )

    exist = grid.exist()

    if exist is False:
        return Response.set(
            warnings=[
                Message(
                    msg=f"Table {table} does not exist in dataset {dataset}",
                    type="NOT_FOUND",
                    loc=["path", "dataset", "table"],
                    ctx={
                        "table": table,
                        "dataset": dataset,
                    }
                )
            ]
        )

    if exist is True:
        grid.drop()

        return Response.set(
            data={
                "exist": grid.exist()
            }
        )


@router.put(
    Endpoints.get("BQ.dataset.table.import"),
    name="Import data int BQ table",
    tags=["BigQuery"],
    operation_id="import_data",
    response_model_exclude_none=True
)
def import_data(
        dataset: BQParams.dataset().type_ = BQParams.dataset().path,
        table: BQParams.table().type_ = BQParams.table().path,
        mode: BQParams.mode().type_ = BQParams.mode().query,
        blob_url: str = Query(
            default=...,
            description="URL of the blob to be imported",
            alias="blobURL",
            example="gs://bucket_name/path/to/file.csv"
        )
):
    grid = Grid(
        name=table,
        dataset=dataset
    )

    exist = grid.exist()

    if exist is False:
        return Response.set(
            warnings=[
                Message(
                    msg=f"Table {table} does not exist in dataset {dataset}",
                    type="NOT_FOUND",
                    loc=["path", "dataset", "table"],
                    ctx={
                        "table": table,
                        "dataset": dataset,
                    }
                )
            ]
        )

    if exist is True:

        errors = []
        load_job = grid.import_data(
            blob_uri=blob_url,
            mode=mode
        )

        if getattr(load_job, "errors", None) is not None:

            for idx, err in enumerate(load_job.errors):

                error_loc = ["query", "blobURL"]
                if "location" in err:
                    error_loc = [err["location"]]

                msg = Message(
                    msg=err["message"],
                    type=err["reason"],
                    loc=error_loc
                )

                Logger.error(
                    err["message"],
                    extra={
                        "reason": err["reason"],
                        "loc": error_loc
                    }
                )

                errors.append(msg)

        if len(errors) > 0:

            return Response.set(
                errors=errors
            )

        else:

            return Response.set(
                data={
                    "exist": grid.exist(),
                    "ref": grid.table_ref._properties
                }
            )
