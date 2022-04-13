import pandas as pd
from dataclasses import dataclasses

# https://docs.google.com/spreadsheets/d/1wsnMLD1jB_Y5LGb32qKPneozJUwvMLMkqq6ZqiMBN0g/edit?usp=sharing
PRESET_FILTERS = {
    0: lambda df: df.year_build > 2005,
    1: lambda df: df.land_use_code == "1001",
}
