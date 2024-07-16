# external packages and objects
from fastapi import APIRouter, Depends, Body, Path, Query
from google.cloud import storage

from surquest.fastapi.schemas.responses import (
    Response,
    Responses,
    Message
)

# internal packages and objects
from .params import GCSParams
from settings import Endpoints
router = APIRouter()


@router.put(
    Endpoints.get("GCS.buckets.blobs.merge"),
    name="Merge blobs",
    tags=["GCS"],
    operation_id="merge_blobs",
    responses=Responses.get(),
    response_model_exclude_none=True
)
def merge_blobs(
    bucket: GCSParams.bucket().type_ = GCSParams.bucket().path,
    src_prefix: GCSParams.prefix().type_ = GCSParams.prefix(**{
                "alias": "srcPrefix",
                "description": "Prefix of blobs to be sourced into merge"
        }).query,
    tmp_prefix: GCSParams.prefix().type_ = GCSParams.prefix(**{
            "alias": "tmpPrefix",
            "description": "Prefix of blobs where temporary chunks are stored"
        }).query,
    final_blob: GCSParams.blob().type_ = GCSParams.blob(**{
            "alias": "finalBlob",
            "description": "Name of final blob"
    }).query,
    chunk_size: int = Query(
        default=31,
        title="Chunk size",
        alias="chunkSize",
        description="Number of blobs to merge in one chunk",
        ge=1,
    )
):

    # get GCS client
    client = storage.Client()
    bucket = bucket.lower()

    # list all paged bq files
    blobs = list(
        client.list_blobs(
            bucket,
            prefix=src_prefix
        )
    )

    if len(blobs) == 0:

        blob = client.bucket(bucket).blob(final_blob)

        return Response.set(
            status_code=299,
            warnings=[
                Message(
                    msg="No blobs found to merge in GCS bucket {bucket} with prefix {prefix}".format(
                        bucket=bucket,
                        prefix=src_prefix
                    ),
                    type="No.Data",
                    ctx={
                        "bucket": bucket,
                        "prefix": src_prefix
                    }
                )
            ],
            data={
                "blob": blob.public_url
            }
        )

    # if number of blobs is less than chunk size
    if len(blobs) <= chunk_size:

        blob = client.bucket(bucket).blob(final_blob)

        blob.compose(blobs)

        return Response.set(
            data={
                "blobURL": blob.public_url
            })

    # if number of blobs is greater than chunk size
    # split detected blobs into chunks
    chunked_blobs = list()
    for i in range(0, len(blobs), chunk_size):
        chunked_blobs.append(
            blobs[i:i + chunk_size]
        )

    # merge blobs into 1
    for index, chunk in enumerate(chunked_blobs):

        if index == 0:

            # merge all blobs in the first chunk
            client.bucket(bucket).blob(
                "{prefix}/part.{index}.jsonl".format(
                    prefix=tmp_prefix,
                    index=str(index).zfill(8)
                )
            ).compose(chunk)

        elif 0 < index <= (len(chunked_blobs) - 1):

            # get blob from previous merged chunk of blobs
            prev_blob = client.bucket(bucket).blob(
                "{prefix}/part.{index}.jsonl".format(
                    prefix=tmp_prefix,
                    index=str((index - 1)).zfill(8)
                )
            )

            # add this blob to the beginning of the current chunk
            chunk.insert(0, prev_blob)

            if index < (len(chunked_blobs) - 1):

                # merge all blobs in the current chunk
                client.bucket(bucket).blob(
                    "{prefix}/part.{index}.jsonl".format(
                        prefix=tmp_prefix,
                        index=str(index).zfill(8)
                    )
                ).compose(chunk)

            if index == (len(chunked_blobs) - 1):

                # if the current chunk is the last one
                # return the merged blob
                blob = client.bucket(bucket).blob(final_blob)
                blob.compose(chunk)

                return Response.set(
                    data={
                        "blobURL": blob.public_url
                    })
