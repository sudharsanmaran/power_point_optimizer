import numpy as np
import pandas as pd
from backend.src.app.services.business_services.metrics.base import (
    calculate_average,
)


def calculate_average_wait_time_by_bucket(
    filtered_df: pd.DataFrame,
) -> pd.DataFrame:
    week_days = [
        " 0 - 30 sec",
        "30 sec - 1 min",
        "1min - 1min 30 sec",
        "1min 30 sec - 2min",
        "2min - 2min 30sec",
        "2min 30sec - 3min",
        "> 3min",
    ]

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


wait_time_metrics = {
    "avg_wait_time_by_bucket": calculate_average_wait_time_by_bucket,
    "avg_wait_time_by_weekday": calculate_average_wait_time_by_weekday,
    "avg_people_in_line_by_bucket": calculate_average_people_in_line_by_bucket,
    "avg_people_in_line_by_weekday": (
        calculate_average_people_in_line_by_weekday
    ),
    "avg_wait_time_by_hour": calculate_average_wait_time_by_hour,
    "wait_time_vs_queue_length": calculate_wait_time_vs_queue_length,
}
