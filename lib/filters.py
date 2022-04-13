import pandas as pd
from dataclasses import dataclasses


FILTERS = {
    0: lambda df: df.year_build > 2005,
    1: lambda df: df.land_use_code == "1001",
}
