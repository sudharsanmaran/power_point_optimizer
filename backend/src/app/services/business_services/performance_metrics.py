from typing import Callable, Dict
import numpy as np
import pandas as pd

from backend.src.app.configs.constants import (
    EVENTS,
    CONFIGS,
    DataForm,
    PerformanceSection,
)
from backend.src.app.services.business_services.errors import EmptyDataError
from backend.src.app.services.business_services.utils import get_enum_values
from backend.src.app.schemas.performance_metrics import Params
from backend.src.app.services.business_services.metrics.wait_time import (
    wait_time_metrics,
)


async def get_history_df():
    """
    Get the historical data DataFrame.

    Returns:
    - pd.DataFrame: The historical data DataFrame.

    Raises:
    - EmptyDataError: If the historical data is not found or invalid format
    """

    if "HISTORICAL_DATA_FRAME" not in CONFIGS:
        raise EmptyDataError("No data found")
    if not isinstance(CONFIGS["HISTORICAL_DATA_FRAME"], pd.DataFrame):
        raise EmptyDataError("Invalid data format")
    return CONFIGS["HISTORICAL_DATA_FRAME"].copy(deep=True)


async def calculate_and_format_metrics(
    data: pd.DataFrame, metric_functions: Dict[str, Callable]
) -> dict:
    """
    Calculate specified metrics on a filtered DataFrame and format the results.

    Parameters:
    - data (pd.DataFrame): The DataFrame containing the filtered data.
    - metric_functions (Dict[str, Callable]): A dictionary
        where keys are metric names and values are functions that compute
        the metric on the DataFrame.

    Returns:
    - dict: A dictionary where keys are metric names
        and values are the results of the metric calculations
        formatted as dictionaries with 'split' orientation.

    Raises:
    - EmptyDataError: If the input DataFrame is empty.
    """

    if data.empty:
        raise EmptyDataError("No data found for the given filters")

    # Calculate metrics and format them as dictionaries
    metric_results = {
        metric_name: func(data).to_dict(orient="split")
        for metric_name, func in metric_functions.items()
    }
    return metric_results


async def filter_df(
    params: Params,
    kpi_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Filter the DataFrame based on the request parameters.

    Parameters:
    - params (Params): The request parameters.
    - kpi_data (pd.DataFrame): The kpi data DataFrame.

    Returns:
    - pd.DataFrame: The filtered DataFrame.

    Raises:
    - EmptyDataError: If no data is found after filtering.
    """

    if kpi_data.empty:
        raise EmptyDataError("No data found")

    filter_mask = True
    if params.cluster:
        # todo: use enum for column names
        filter_mask &= kpi_data["new_clusters"] == params.cluster
    if params.store:
        filter_mask &= kpi_data["store_name"].isin(params.store)
    if params.lane_types:
        filter_mask &= kpi_data["type_of_checkout"].isin(
            get_enum_values(params.lane_types)
        )
    if params.peak_hour:
        filter_mask &= kpi_data["peak_hour"].isin(params.peak_hour)
    if params.covid_flag:
        filter_mask &= kpi_data["Covid_Effect"] == 1
    if params.events_flag:
        filter_mask &= kpi_data["event"].isin(EVENTS)
    if params.total_year_flag:
        filter_mask &= kpi_data["date"]
    if params.october_flag:
        # todo: typecast while reading the data
        kpi_data["date"] = kpi_data["date"].astype(np.datetime64)
        filter_mask &= kpi_data["date"].dt.month == 10

    filtered_df = kpi_data[filter_mask]
    return filtered_df


# Dictionary to map the data form to the function that retrieves the data
data_form_and_df_map = {DataForm.HISTORICAL: get_history_df}
# Dictionary to hold the calculated metrics
metric_calculations = {PerformanceSection.WAIT_TIME: wait_time_metrics}


async def compute_metrics(params: Params) -> Dict:
    """
    Process the performance metrics request and return the performance data.

    Parameters:
    - params (Params): The request parameters.

    Returns:
    - dict: A dictionary containing the performance data.
    """

    get_df_func = data_form_and_df_map[params.data_form]
    required_metric_calculations = metric_calculations[params.type]
    kpi_data = await get_df_func()
    filtered_df = await filter_df(kpi_data=kpi_data, params=params)
    performance_data = await calculate_and_format_metrics(
        filtered_df=filtered_df, metric_functions=required_metric_calculations
    )
    return performance_data
