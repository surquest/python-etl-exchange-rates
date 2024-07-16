import os
from surquest.utils.config.formatter import Formatter
from surquest.utils.loader import Loader

__all__ = ["formatter", "FX"]

formatter = Formatter(
    config=Formatter.import_config(
        configs={
            "GCP": F"{os.getenv('HOME')}/config/config.cloud.google.env.{os.getenv('ENVIRONMENT','PROD')}.json",
            "services": F"{os.getenv('HOME')}/config/config.cloud.google.services.json",
            "solution": F"{os.getenv('HOME')}/config/config.solution.json",
        }
    ),
    naming_patterns=Formatter.load_json(
        path=F"{os.getenv('HOME')}/config/naming.patterns.json"
    )
)


class FX:

    fx_config = Loader.load_json(
        f"{os.getenv('PROJECT_DIR')}/config/subjects/fx.currencies.json"
    ).get("currencies")

    @classmethod
    def get(cls, currency):
        for pair in cls.fx_config:
            if pair.get("code") == currency:
                return pair
        return None


class Endpoints:

    PATHS = {
        "BQ.dataset.table.exist": "/BQ/datasets/{dataset}/tables/{table}/exist",
        "BQ.dataset.table.create": "/BQ/datasets/{dataset}/tables/{table}/create",
        "BQ.dataset.table.drop": "/BQ/datasets/{dataset}/tables/{table}/drop",
        "BQ.dataset.table.truncate": "/BQ/datasets/{dataset}/tables/{table}/truncate",
        "BQ.dataset.table.import": "/BQ/datasets/{dataset}/tables/{table}/import",
        "BQ.dataset.table.records.last": "/BQ/datasets/{dataset}/tables/{table}/records/last",
        "GCS.buckets.blobs.merge": "/GCS/buckets/{bucket}/blobs/*/merge",
        "ETL.config": "/ETL/config",
        "ETL.subjects": "/ETL/subjects",
        "ETL.data.fetch": "/ETL/data/fetch",
        "ETL.batches": "/ETL/batches"

    }

    @classmethod
    def get(cls, name):

        return cls.PATHS.get(name)

