import io

import geopandas as gpd
import pandas as pd
import pyarrow.parquet as pq
import s3fs
from flask import Flask, request

from protopython.proto import query_pb2

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


def shape_filter(dataframe: pd.DataFrame, shapes: list) -> pd.DataFrame:
    """
    Filter a pandas dataframe using a list of shapes

    Args:
        dataframe (pd.DataFrame): The dataframe to filter
        shapes (list): List of shapes

    Returns:
        pd.DataFrame: 
    """
    gdf = gpd.GeoDataFrame(
        dataframe,
        geometry=gpd.points_from_xy(dataframe.situslongitude, dataframe.situslatitude),
    )

    for i, shape in enumerate(shapes):
        if i == 0:
            shape_filter = gdf.within(shape)
        else:
            shape_filter &= gdf.within(shape)

    return pd.DataFrame(gdf[shape_filter])


@APP.route("/count-properties", methods=["GET", "POST"])
def get_request():
    # We use the proto object to read and write the responses
    query_parameters = query_pb2.QueryProperties()
    query_parameters.ParseFromString(request.data)

    print(query_parameters)

    df = load_dataframe()

    df = shape_filter(df, [query_parameters.shape])

    # Not implemented
    # df = apply_preset_filters(df, query_parameters.preset_filter)
    # df = apply_filters(df, query_parameters.filters)

    query_response = query_pb2.QueryCountResponse()
    query_response.count = 42

    return query_response.SerializeToJson()


if __name__ == "__main__":
    APP.run(debug=True)
