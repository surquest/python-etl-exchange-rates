from enum import Enum
from fastapi import Path, Query
from surquest.fastapi.utils.args import QueryConfig, PathConfig


class GCSParams(object):

    @staticmethod
    def bucket(**config):

        defaults = {
            "alias": "bucket",
            "description": "Bucket name"
        }

        if config:
            defaults.update(config)

        return PathConfig(
            type_=str,
            path=Path(
                **defaults
            )
        )

    @staticmethod
    def blob(**config):

        defaults = {
            "alias": "blob",
            "description": "Blob name"
        }

        if config:
            defaults.update(config)

        return QueryConfig(
            type_=str,
            query=Query(
                **defaults
            )
        )

    @staticmethod
    def prefix(**config):

        defaults = {
            "alias": "prefix",
            "description": "Blob prefix"
        }

        if config:
            defaults.update(config)

        return QueryConfig(
            type_=str,
            query=Query(
                **defaults
            )
        )
