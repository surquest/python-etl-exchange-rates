# external packages
import os
import datetime as dt
from google.cloud import storage
from fastapi.testclient import TestClient
from surquest.utils.loader import Loader

# internal packages
from main import app
from settings import Endpoints, FX, formatter

client = TestClient(app)


class TestETL:

    currency = "EUR"
    history_start = dt.datetime.strptime(
        FX.get(currency).get("history").get("start"),
        "%Y-%m-%d"
    ).date()
    table_conf = Loader.load_yaml(
        path=F"{os.getenv('HOME')}/config/subjects/fx.BQ-table.yaml"
    )

    table_conf["name"] = "test"

    def test_etl(self):

        # run ETL in test mode
        config = self.get_config()

        # check if BQ dataset and table exist
        table_exist = self.bq_dataset_table_exist(
            dataset=config.get("BQ").get("dataset"),
            table=self.table_conf["name"]
        )

        # if table exists, delete it
        if table_exist.get("exist") is True:

            self.bq_dataset_table_drop(
                dataset=config.get("BQ").get("dataset"),
                table=self.table_conf["name"]
            )

        # create table
        self.bq_dataset_table_create(
            dataset=config.get("BQ").get("dataset"),
            table=self.table_conf["name"],
            config=self.table_conf
        )

        # check if table exists
        table_exist = self.bq_dataset_table_exist(
            dataset=config.get("BQ").get("dataset"),
            table=self.table_conf["name"]
        )
        assert True == table_exist.get("exist")

        # get last record from BQ table (should be history start date)
        # because table is empty
        last_record = self.bq_dataset_table_records_last(
            dataset=config.get("BQ").get("dataset"),
            table=self.table_conf["name"],
            currency=self.currency
        )

        assert self.history_start == dt.datetime.strptime(
            last_record.get("start").get("date"),
            "%Y-%m-%dT%H:%M:%S"
        ).date()

        # insert records into BQ table
        self.bq_dataset_table_records_insert(
            dataset=config.get("BQ").get("dataset"),
            table=self.table_conf["name"]
        )

        # get last record from BQ table (should be after history start date)
        # because table is NOT empty
        last_record = self.bq_dataset_table_records_last(
            dataset=config.get("BQ").get("dataset"),
            table=self.table_conf["name"],
            currency=self.currency
        )

        assert self.history_start < dt.datetime.strptime(
            last_record.get("start").get("date"),
            "%Y-%m-%d"
        ).date()

        # truncate BQ table
        self.bq_dataset_table_truncate(
            dataset=config.get("BQ").get("dataset"),
            table=self.table_conf["name"]
        )

        # get last record from BQ table (should be history start date)
        # because table is empty
        last_record = self.bq_dataset_table_records_last(
            dataset=config.get("BQ").get("dataset"),
            table=self.table_conf["name"],
            currency=self.currency
        )

        assert self.history_start == dt.datetime.strptime(
            last_record.get("start").get("date"),
            "%Y-%m-%dT%H:%M:%S"
        ).date()



    def get_config(self):

        response = client.get(
            url=Endpoints.get("ETL.config"),
            params={
                "currency": self.currency
            }
        )

        assert 200 == response.status_code
        assert "success" == response.json().get("info").get("status")
        assert self.currency == response.json().get("data").get("ETL").get("currency").get("code")

        return response.json().get("data")

    @staticmethod
    def bq_dataset_table_exist( dataset, table):

        response = client.get(
            url=Endpoints.get("BQ.dataset.table.exist").format(
                dataset=dataset,
                table=table
            )
        )
        assert 200 == response.status_code
        assert "success" == response.json().get("info").get("status")
        return response.json().get("data")

    @staticmethod
    def bq_dataset_table_drop(dataset, table):

        response = client.delete(
            url=Endpoints.get("BQ.dataset.table.drop").format(
                dataset=dataset,
                table=table
            )
        )
        assert 200 == response.status_code
        assert "success" == response.json().get("info").get("status")
        return response.json()

    @staticmethod
    def bq_dataset_table_truncate(dataset, table):
        response = client.patch(
            url=Endpoints.get("BQ.dataset.table.truncate").format(
                dataset=dataset,
                table=table
            )
        )
        assert 200 == response.status_code
        assert "success" == response.json().get("info").get("status")
        return response.json()

    @staticmethod
    def bq_dataset_table_create(dataset, table, config):
        response = client.post(
            url=Endpoints.get("BQ.dataset.table.create").format(
                dataset=dataset,
                table=table
            ),
            json = config
        )
        assert 201 == response.status_code
        assert "success" == response.json().get("info").get("status")
        return response.json().get("data")

    @staticmethod
    def bq_dataset_table_records_last(dataset, table, currency):

        response = client.get(
            url=Endpoints.get("BQ.dataset.table.records.last").format(
                dataset=dataset,
                table=table
            ),
            params={
                "currency": currency
            }
        )
        assert 200 == response.status_code
        assert "success" == response.json().get("info").get("status")
        return response.json().get("data")

    @staticmethod
    def bq_dataset_table_records_insert(dataset, table):

        # import data into table

        # -> upload file to GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(formatter.get("storage.buckets.ingress").replace("test", "prod"))
        blob = bucket.blob("test.data.jsonl")
        blob.upload_from_filename(F"{os.getenv('HOME')}/data/sample/fx.eur-usd.jsonl")

        # -> import data into table
        response = client.put(
            url=Endpoints.get("BQ.dataset.table.import").format(
                dataset=dataset,
                table=table
            ),
            params={
                "mode": "WRITE_TRUNCATE",
                "blobURL": blob.public_url
            }
        )

        assert 200 == response.status_code
        assert "success" == response.json().get("info").get("status")

    def test__bq_dataset_table__import__errors(self):

        # run ETL in test mode
        config = self.get_config()

        # check if BQ dataset and table exist
        table_exist = self.bq_dataset_table_exist(
            dataset=config.get("BQ").get("dataset"),
            table=self.table_conf["name"]
        )

        # if table exists, delete it
        if table_exist.get("exist") is True:
            self.bq_dataset_table_drop(
                dataset=config.get("BQ").get("dataset"),
                table=self.table_conf["name"]
            )

        # create table
        self.bq_dataset_table_create(
            dataset=config.get("BQ").get("dataset"),
            table=self.table_conf["name"],
            config=self.table_conf
        )

        # -> upload file to GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(
            formatter.get("storage.buckets.ingress").replace("test", "prod"))
        blob = bucket.blob("test.invalid.data.jsonl")
        blob.upload_from_filename(
            F"{os.getenv('HOME')}/data/sample/fx.eur-usd.invalid.jsonl")

        # -> import data into table
        response = client.put(
            url=Endpoints.get("BQ.dataset.table.import").format(
                dataset=config.get("BQ").get("dataset"),
                table=self.table_conf["name"]
            ),
            params={
                "mode": "WRITE_TRUNCATE",
                "blobURL": blob.public_url
            }
        )

        assert 500 == response.status_code
        assert "error" == response.json().get("info").get("status")


    def test__data_fetch__success(self):

        # get GCS config
        config = self.get_config().get("GCS")
        config["bucket"] = config["bucket"].replace("test", "prod")

        # get data from Binance API
        response = client.post(
            url=Endpoints.get("ETL.data.fetch"),
            params={
                "start": "2023-04-01",
                "end": "2023-04-02",
                "currency": self.currency
            },
            json=config

        )

        assert 200 == response.status_code
        assert "success" == response.json().get("info").get("status")


    def test__get_batches__success(self):

        response = client.get(
            url=Endpoints.get("ETL.batches"),
            params={
                "start": "2023-04-01",
                "end": "2023-04-02",
                "size": 100
            }
        )

        assert 200 == response.status_code
        assert "success" == response.json().get("info").get("status")
