from typing import List
import numpy as np
import pandas as pd

from backend.src.app.configs.constants import (
    EVENTS,
    CONFIGS,
    DataForm,
    LaneType,
    PerformanceSection,
)
from backend.src.app.configs.errors import EmptyDataError
from backend.src.app.schemas.review_k_p_i import Params


async def get_history_df():
    return CONFIGS["HISTORICAL_DATA_FRAME"].copy(deep=True)


def get_time_buckets():
    return [
        " 0 - 30 sec",
        "30 sec - 1 min",
        "1min - 1min 30 sec",
        "1min 30 sec - 2min",
        "2min - 2min 30sec",
        "2min 30sec - 3min",
        "> 3min",
    ]


def calculate_average(data, group_by_cols, target_col, index_labels):
    """Helper function to calculate the average and reindex."""
    pivot_data = data.groupby(group_by_cols)[[target_col]].mean().unstack()
    pivot_data.columns = pivot_data.columns.get_level_values(1)
    pivot_data.reset_index(inplace=True)
    pivot_data = pivot_data.set_index(group_by_cols[0])
    pivot_data = pivot_data.reindex(index_labels, fill_value=0).reset_index()
    return pivot_data.replace(np.nan, 0)


def calculate_average_wait_time_by_bucket(
    filtered_df: pd.DataFrame,
) -> pd.DataFrame:
    week_days = get_time_buckets()
    avg_wait_time_data = calculate_average(
        filtered_df,
        ["Wait_Time_BKT", "type_of_checkout"],
        "avg_waiting_time_Tq",
        week_days,
    )
    return avg_wait_time_data


def calculate_average_wait_time_by_weekday(
    filtered_df: pd.DataFrame,
) -> pd.DataFrame:
    week_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    avg_wait_time_weekday_data = calculate_average(
        filtered_df,
        ["weekday_name", "type_of_checkout"],
        "avg_waiting_time_Tq",
        week_days,
    )
    return avg_wait_time_weekday_data


def calculate_average_people_in_line_by_bucket(
    filtered_df: pd.DataFrame,
) -> pd.DataFrame:
    # Define the buckets for categorizing the number of people in line
    buckets = ["1", "3", "5", "7", "9", "11", "> 11"]

    # Create a new column 'Shoppers_BKT' based on
    # the 'avg_num_wait_queue_Nq' values
    filtered_df["Shoppers_BKT"] = np.select(
        [
            filtered_df["avg_num_wait_queue_Nq"] <= 1,
            filtered_df["avg_num_wait_queue_Nq"] <= 3,
            filtered_df["avg_num_wait_queue_Nq"] <= 5,
            filtered_df["avg_num_wait_queue_Nq"] <= 7,
            filtered_df["avg_num_wait_queue_Nq"] <= 9,
            filtered_df["avg_num_wait_queue_Nq"] <= 11,
        ],
        ["1", "3", "5", "7", "9", "11"],
        default="> 11",
    )

    # Use 'avg_num_wait_queue_Nq' for calculating the average, which is numeric
    avg_people_line_data = (
        filtered_df.groupby(["Shoppers_BKT", "type_of_checkout"])[
            "avg_num_wait_queue_Nq"
        ]
        .mean()
        .unstack()
    )

    # Reset the index and reindex to ensure all buckets are present
    avg_people_line_data.reset_index(inplace=True)
    avg_people_line_data = avg_people_line_data.set_index("Shoppers_BKT")
    avg_people_line_data = avg_people_line_data.reindex(
        buckets, fill_value=0
    ).reset_index()

    return avg_people_line_data


def calculate_average_wait_time_by_hour(
    filtered_df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate and prepare data for the average wait time by hour graph."""
    # Group by hour and type_of_checkout, then calculate the average wait time
    avg_wait_time_hourly_data = (
        filtered_df.groupby(["hour", "type_of_checkout"])[
            "avg_waiting_time_Tq"
        ]
        .mean()
        .unstack()
    )
    avg_wait_time_hourly_data.reset_index(inplace=True)
    avg_wait_time_hourly_data = avg_wait_time_hourly_data.fillna(0)
    return avg_wait_time_hourly_data


def calculate_wait_time_vs_queue_length(
    filtered_df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate and prepare data for the wait time vs. queue length graph."""
    # Group by hour and type_of_checkout, then calculate the average wait time
    # and queue length
    wait_time_vs_queue_data = (
        filtered_df.groupby(["hour", "type_of_checkout"])
        .agg(
            avg_wait_time=("avg_waiting_time_Tq", "mean"),
            avg_queue_length=("avg_num_wait_queue_Nq", "mean"),
        )
        .unstack()
    )
    wait_time_vs_queue_data.reset_index(inplace=True)
    wait_time_vs_queue_data = wait_time_vs_queue_data.fillna(0)
    return wait_time_vs_queue_data


def calculate_average_people_in_line_by_weekday(
    filtered_df: pd.DataFrame,
) -> pd.DataFrame:
    week_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    avg_people_weekday_data = calculate_average(
        filtered_df,
        ["weekday_name", "type_of_checkout"],
        "avg_num_wait_queue_Nq",
        week_days,
    )
    return avg_people_weekday_data


async def get_wait_time(filtered_df: pd.DataFrame) -> dict:
    if filtered_df.empty:
        raise EmptyDataError("No data found for the given filters")

    # Dictionary to hold the calculated metrics
    metric_calculations = {
        "avg_wait_time_by_bucket": calculate_average_wait_time_by_bucket,
        "avg_wait_time_by_weekday": calculate_average_wait_time_by_weekday,
        "avg_people_in_line_by_bucket": (
            calculate_average_people_in_line_by_bucket
        ),
        "avg_people_in_line_by_weekday": (
            calculate_average_people_in_line_by_weekday
        ),
        "avg_wait_time_by_hour": calculate_average_wait_time_by_hour,
        "wait_time_vs_queue_length": calculate_wait_time_vs_queue_length,
    }

    # Calculate metrics and format them as dictionaries
    wait_time_kpi_values = {
        metric_name: func(filtered_df).to_dict(orient="split")
        for metric_name, func in metric_calculations.items()
    }
    return wait_time_kpi_values


def extract_unique_lane_types(filtered_df: pd.DataFrame) -> List[str]:
    return list(filtered_df["type_of_checkout"].unique())


async def filter_df(
    params: Params,
    get_df: callable = get_history_df,
) -> pd.DataFrame:

    kpi_data = await get_df()

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
            get_lane_type_values(params.lane_types)
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
        kpi_data["date"] = kpi_data["date"].astype(np.datetime64)
        filter_mask &= kpi_data["date"].dt.month == 10

    filtered_df = kpi_data[filter_mask]
    # todo: separate this into a function
    filtered_df.rename(columns={"total": "total_co"}, inplace=True)
    return filtered_df


def get_lane_type_values(lane_types: List[LaneType]):
    return [lane_type.value for lane_type in lane_types]


# maps
performance_type_functions_map = {PerformanceSection.WAIT_TIME: get_wait_time}
data_form_get_df_map = {DataForm.HISTORICAL: get_history_df}


async def process_review_k_p_i(params: Params):
    performance_type_function = performance_type_functions_map[params.type]
    get_df_func = data_form_get_df_map[params.data_form]

    filtered_df = await filter_df(get_df=get_df_func, params=params)
    performance_data = await performance_type_function(filtered_df=filtered_df)
    return performance_data
