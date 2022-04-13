import httplib
import pyarrow.parquet as pq
import s3fs

import pandas as pd
from flask import Flask, request
from protopython.proto import query_pb2
import io


APP = Flask(__name__)
CACHED_DATA: pd.DataFrame
S3 = s3fs.S3FileSystem()
BASE_S3_DIR = "s3://lendinghome-data-sagemaker/innovation-arv-estimator"


def load_dataframe(path: str) -> pd.DataFrame:
    """
    Read a parquet file from S3

    Args:
        path (str): The path to read

    Returns:
        pd.Dataframe: The parquet file in padnas dataframe
    """
    if CACHED_DATA is None:
        CACHED_DATA = pq.ParquetDataset(path, filesystem=S3).read_pandas().to_pandas()

    return CACHED_DATA.copy()


@APP.route("/count-properties", methods=["GET", "POST"])
def get_request():
    # We use the proto object to read and write the responses
    query_parameters = query_pb2.QueryProperties()

    query_parameters.ParseFromString(request.data)

    print(query_parameters)

    query_response = query_pb2.QueryCountResponse()
    query_response.count = 42

    return query_response.SerializeToJson(), httplib.OK


if __name__ == "__main__":
    APP.run(debug=True)
