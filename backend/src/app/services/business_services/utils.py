from enum import Enum
from typing import List, TypeVar

import pandas as pd


T = TypeVar("T", bound=Enum)


def get_enum_values(enum_list: List[T]) -> List:
    return [enum_item.value for enum_item in enum_list]


def extract_unique_values(series: pd.Series) -> List:
    return list(series.unique())
