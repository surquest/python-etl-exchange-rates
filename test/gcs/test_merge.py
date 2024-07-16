# external packages
import os
import pytest
from google.cloud import storage
from fastapi.testclient import TestClient

# internal packages
from main import app
from settings import Endpoints, FX, formatter

client = TestClient(app)


class TestGCS:

    client = storage.Client()
    bucket_name = formatter.get("storage.buckets.ingress").replace("test", "prod")
    bucket=client.bucket(bucket_name)


    def test__merge__one_file(self):

        src_prefix = "test/one/bq/"
        tmp_prefix = "test/one/tmp/"
        final_blob = "test/one/final.jsonl"
        blob = self.bucket.blob(f"{src_prefix}part.1.jsonl")
        blob.upload_from_filename(
            F"{os.getenv('HOME')}/data/sample/fx.eur-usd.jsonl"
        )

        response = client.put(
            url=Endpoints.get("GCS.buckets.blobs.merge").format(
                bucket=self.bucket_name
            ),
            params={
                "srcPrefix":src_prefix,
                "tmpPrefix":tmp_prefix,
                "finalBlob":final_blob
            }
        )

        assert 200 == response.status_code
        assert "success" == response.json().get("info").get("status")

        # get the final blob from GCS
        blob = self.bucket.blob(final_blob)

        # check number of lines in the final blob
        assert 2 == len(blob.download_as_string().decode("utf-8").splitlines())



    @pytest.mark.parametrize("files, lines", [(3, 6), (10,20), (50,100)])
    def test__merge__more_file(self, files, lines):

        src_prefix = F"test/more/{files}/bq/"
        tmp_prefix = F"test/more/{files}/tmp/"
        final_blob = F"test/more/{files}/final.jsonl"

        for i in range(1, files + 1):
            blob = self.bucket.blob(f"{src_prefix}part.{i}.jsonl")
            blob.upload_from_filename(
                F"{os.getenv('HOME')}/data/sample/fx.eur-usd.jsonl"
            )

        response = client.put(
            url=Endpoints.get("GCS.buckets.blobs.merge").format(
                bucket=self.bucket_name
            ),
            params={
                "srcPrefix":src_prefix,
                "tmpPrefix":tmp_prefix,
                "finalBlob":final_blob
            }
        )

        assert 200 == response.status_code, "Status code is not 200"
        assert "success" == response.json().get("info").get("status")

        # get the final blob from GCS
        blob = self.bucket.blob(final_blob)

        # check number of lines in the final blob
        assert lines == len(blob.download_as_string().decode("utf-8").splitlines()), \
        F"Number of lines in the final blob is not {lines}"

