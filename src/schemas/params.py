from dataclasses import dataclass
from fastapi import Path, Query
from surquest.fastapi.utils.args import QueryConfig, PathConfig

from enums.currencies import Currencies


@dataclass
class Prefixes:
    raw: str
    bq: str
    tmp: str


@dataclass
class Blobs:

    merged: str


@dataclass
class GCS:
    bucket: str
    blobs: Blobs
    prefixes: Prefixes


class Params(object):

    @staticmethod
    def bucket(**config):

        defaults = {
            "alias": "bucket",
            "description": "GCS bucket name"
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
    def currency(**config):

        defaults = {
            "alias": "currency",
            "description": "Currency, e.g. USD",
        }

        if config:
            defaults.update(config)

        return QueryConfig(
            type_=Currencies,
            query=Query(
                **defaults
            )
        )

    @staticmethod
    def dataset(**config):

        defaults = {
            "alias": "dataset",
            "description": "Dataset name"
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
    def table(**config):

        defaults = {
            "alias": "table",
            "description": "Table name"
        }

        if config:
            defaults.update(config)

        return PathConfig(
            type_=str,
            path=Path(
                **defaults
            )
        )
