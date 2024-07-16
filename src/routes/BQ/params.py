from enum import Enum
from fastapi import Path, Query
from surquest.fastapi.utils.args import QueryConfig, PathConfig


class Mode(str, Enum):

    WRITE_TRUNCATE = "WRITE_TRUNCATE"
    WRITE_APPEND = "WRITE_APPEND"
    WRITE_EMPTY = "WRITE_EMPTY"


class BQParams(object):

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

    @staticmethod
    def mode(**config):

        defaults = {
            "alias": "mode",
            "description": "Mode of the import",
            "default": Mode.WRITE_APPEND.value
        }

        if config:
            defaults.update(config)

        return QueryConfig(
            type_=Mode,
            query=Query(
                **defaults
            )
        )
