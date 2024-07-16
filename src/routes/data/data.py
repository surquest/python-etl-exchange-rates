# external packages and objects
import datetime as dt
import requests
import json
from fastapi import APIRouter, Depends, Body, Path, Query
from google.cloud import bigquery, storage

from surquest.GCP.secret_assessor import Secret
from surquest.fastapi.utils.GCP.logging import Logger
from surquest.fastapi.schemas.responses import (
    Response,
    Responses,
    Message
)

# internal packages and objects
from schemas.params import Params, GCS
from settings import formatter, FX, Endpoints

router = APIRouter()


@router.get(
    Endpoints.get("BQ.dataset.table.records.last"),
    name="Get timestamp of last record",
    tags=["BigQuery"],
    operation_id="get_timestamp_of_last_record",
    responses=Responses.get(),
    response_model_exclude_none=True
)
def get_timestamp_of_last_record(
        dataset: Params.dataset().type_ = Params.dataset().path,
        table: Params.table().type_ = Params.table().path,
        currency: Params.currency().type_ = Params.currency().query
):
    """Method returns the timestamp of the last record in the given table
    for the given currency pair.

    * **dataset**: name of the dataset
    * **table**: name of the table
    * **currency**: currency pair, e.g. BITCOIN-USD
    """
    # get currency pair configuration
    fx = FX.get(currency=currency.value)

    # prepare SQL query for getting the latest date_time
    # for the given currency pair
    sql = """
        SELECT max(date) as date
        FROM `{project}.{dataset}.{table}`
        WHERE currency_base = @currency_base
    """.format(
        project=formatter.config.get("GCP").get("id"),
        dataset=dataset,
        table=table,
    )

    # get BQ client
    client = bigquery.Client()

    # prepare bigquery job with the SQL query and parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "currency_base", "STRING", currency.value
            )
        ]
    )

    # run the query
    query_job = client.query(
        query=sql,
        job_config=job_config
    )

    # get the result
    results = query_job.result()

    # if no data is returned, return the default value
    start = dt.datetime.strptime(
        fx.get("history").get("start"), "%Y-%m-%d"
    )

    if results.total_rows >= 1:
        for row in results:
            if row.date is not None:
                start = row.date

    # return start date time in ISO format and timestamp
    return Response.set(
        data={
            "start": {
                "date": start
            }
        }
    )


@router.get(
    Endpoints.get("ETL.batches"),
    name="Get list of batches",
    tags=["ETL"],
    operation_id="get_batches",
    responses=Responses.get(),
    response_model_exclude_none=True
)
def get_batches(
        start: dt.date = Query(
            default=...,
            alias="start",
            title="Start of the range for batches",
            description="Start of the range for batches (date in ISO format)"
        ),
        end: dt.date = Query(
            default=dt.date.today(),
            alias="end",
            title="End of the range for batches",
            description="End of the range for batches (date in ISO format)"
        ),
        size: int = Query(
            default=2*365,  # 2 years
            alias="size",
            title="Size of the batches",
            description="Size of the batches in days",
            ge=1
        )
):
    """Method returns a list of batches for the given range.

    * **start**: start of the range for batches (UTC timestamp)
    * **end**: end of the range for batches (UTC timestamp)
    * **size**: size of the batches in seconds

    Returns
    """

    batches = []

    # get batches for the given range and size
    days = (end - start).days + 1
    for idx, batch in enumerate(range(0, days, size)):

        # # get start and end of the batch
        # # add 1 day to the start of the batch
        batch_start = start + dt.timedelta(days=batch+1)
        batch_end = batch_start + dt.timedelta(days=size-1)

        # if batch end is greater than the end of the range
        if batch_end > end:
            batch_end = end

        if batch_start <= end:

            batches.append({
                "start": batch_start,
                "end": batch_end
            })

    return Response.set(
        data=batches
    )


@router.post(
    Endpoints.get("ETL.data.fetch"),
    name="Fetch data from Exchange Rates API",
    tags=["ETL"],
    operation_id="fetch_data",
    responses=Responses.get(),
    response_model_exclude_none=True
)
def fetch_data(
        start: dt.date = Query(
            default=...,
            alias="start",
            title="Start of the range for batches",
            description="Start of the range for batches (date in ISO format)"
        ),
        end: dt.date = Query(
            default=dt.datetime.today().strftime("%Y-%m-%d"),
            alias="end",
            title="End of the range for batches",
            description="End of the range for batches (date in ISO format)"
        ),
        currency: Params.currency().type_ = Params.currency().query,
        GCS: GCS = Body(...)
):
    # prepare variables
    data = {"bq": []}
    client = storage.Client()
    bucket = client.bucket(GCS.bucket)
    dt_format = "%Y-%m-%d"
    paths = {
        "raw": "{prefix}/part.{start}.{end}.json".format(
            prefix=GCS.prefixes.raw,
            start=start.strftime(dt_format),
            end=end.strftime(dt_format),
        ),
        "bq": "{prefix}/part.{start}.{end}.jsonl".format(
            prefix=GCS.prefixes.bq,
            start=start.strftime(dt_format),
            end=end.strftime(dt_format),
        )
    }
    blobs = {
        "raw": bucket.blob(paths.get("raw")),
        "bq": bucket.blob(paths.get("bq"))
    }

    # get currency pair configuration
    fx = FX.get(currency=currency.value)

    # fetch data from Binance API
    endpoint = fx.get("endpoints").get("timeseries").format(
        code=fx.get("code"),
        startDate=start,
        endDate=end
    )

    Logger.debug(
        "Fetching data from ExchangeRate API: %s",
        endpoint
    )

    # fetch data from: https://api.exchangerate.host
    response = requests.get(
        url=endpoint,
        headers={
            "apikey": Secret.get(formatter.get("secrets.misc.apiKey"))
        }
    )

    Logger.debug(
        "ExchangeRate API response code: %s",
        response.status_code
    )

    if response.status_code != 200:
        return Response.set(
            errors=[
                Message(
                    msg="ExchangeRate API returned an error",
                    type="ExchangeRate.API.Error",
                    ctx={
                        "code": response.status_code,
                        "error": response.text
                    }
                )
            ],
            status_code=response.status_code
        )

    # upload raw data to GCS
    blobs.get("raw").upload_from_string(
        response.text,
        content_type = "application/json"
    )

    raw_data = response.json().get("rates")
    Logger.debug(
        "Count of raw data entries: %s",
        len(raw_data)
    )

    if len(raw_data.keys()) > 0:
        # prepare data for BigQuery table (JSON Lines format)
        for date in raw_data:

            for currency_quote in raw_data.get(date):

                exchange_rate = raw_data.get(date).get(currency_quote)

                data.get("bq").append(
                    json.dumps({
                        "date":date, # ISO format
                        "currency_base": currency.value,
                        "currency_quote": currency_quote,
                        "exchange_rate": exchange_rate,
                        "created_at": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
                    })
                )

        # upload data to GCS
        blobs.get("bq").upload_from_string(
            "\n".join(data.get("bq")) + "\n",
            content_type="application/json-lines"
        )

    return Response.set(
        data={
            "blobs":{
                "raw": blobs.get("raw").public_url,
                "bq": blobs.get("bq").public_url
            },
            "numRows": len(data.get("bq"))
        }
    )
