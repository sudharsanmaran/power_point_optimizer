# import pytest
# import pandas as pd
# from unittest.mock import patch
# from backend.src.app.configs.constants import (
#     DataForm,
#     LaneType,
#     PerformanceSection,
# )
# from backend.src.app.configs.errors import EmptyDataError
# from backend.src.app.schemas.review_k_p_i import Params
# from backend.src.app.services.core.review_k_p_i import (
#     calculate_average_people_in_line_by_bucket,
#     calculate_average_people_in_line_by_weekday,
#     calculate_average_wait_time_by_bucket,
#     calculate_average_wait_time_by_hour,
#     calculate_average_wait_time_by_weekday,
#     calculate_wait_time_vs_queue_length,
#     extract_unique_lane_types,
#     filter_df,
#     get_history_df,
#     get_lane_type_values,
#     get_wait_time,
#     process_review_k_p_i,
# )


# # Test for calculate_average_wait_time_by_bucket
# def test_calculate_average_wait_time_by_bucket():
#     data = pd.DataFrame(
#         {
#             "Wait_Time_BKT": [" 0 - 30 sec", "30 sec - 1 min"],
#             "type_of_checkout": ["self", "self"],
#             "avg_waiting_time_Tq": [10, 20],
#         }
#     )
#     result = calculate_average_wait_time_by_bucket(data)
#     assert "self" in result.columns
#     assert result["self"].tolist() == [10, 20, 0, 0, 0, 0, 0]


# # Async test for filter_df
# @pytest.mark.asyncio
# async def test_filter_df():
#     params = Params(
#         cluster=1,
#         store=[11],
#         lane_types=[LaneType.MANNED_TRADITIONAL],
#         peak_hour=[1],
#         covid_flag=True,
#     )
#     kpi_data = pd.DataFrame(
#         {
#             "new_clusters": [1, 2],
#             "store_name": [11, 22],
#             "type_of_checkout": [
#                 LaneType.MANNED_TRADITIONAL.value,
#                 LaneType.MANNED_EXPRESS.value,
#             ],
#             "peak_hour": [1, 2],
#             "Covid_Effect": [1, 0],
#             "event": ["Event1", "Event2"],
#             "date": pd.to_datetime(["2023-10-01", "2023-10-02"]),
#         }
#     )
#     result = await filter_df(params=params, kpi_data=kpi_data)
#     assert result.shape[0] == 1
#     assert result["new_clusters"].tolist() == [1]
#     assert result["store_name"].tolist() == [11]
#     assert result["type_of_checkout"].tolist() == [
#         LaneType.MANNED_TRADITIONAL.value
#     ]
#     assert result["peak_hour"].tolist() == [1]
#     assert result["Covid_Effect"].tolist() == [1]
#     assert result["event"].tolist() == ["Event1"]
#     assert result["date"].tolist() == [pd.Timestamp("2023-10-01")]


from enum import Enum
import pytest
import pandas as pd
import numpy as np
from unittest.mock import AsyncMock, patch, MagicMock
from backend.src.app.configs.constants import (
    DataForm,
    LaneType,
    PerformanceSection,
)
from backend.src.app.errors import EmptyDataError
from backend.src.app.schemas.performance_metrics import Params
from backend.src.app.services.core.review_k_p_i import (
    calculate_average_people_in_line_by_bucket,
    calculate_average_people_in_line_by_weekday,
    calculate_average_wait_time_by_bucket,
    calculate_average_wait_time_by_hour,
    calculate_average_wait_time_by_weekday,
    calculate_wait_time_vs_queue_length,
    extract_unique_lane_types,
    filter_df,
    get_history_df,
    get_lane_type_values,
    process_metric_calculation_and_format_into_split,
    process_review_k_p_i,
)


# Test for calculate_average_wait_time_by_weekday
def test_calculate_average_wait_time_by_weekday():
    data = pd.DataFrame(
        {
            "weekday_name": ["Monday", "Tuesday"],
            "type_of_checkout": ["self", "self"],
            "avg_waiting_time_Tq": [15, 25],
        }
    )
    result = calculate_average_wait_time_by_weekday(data)
    assert "self" in result.columns
    assert result["self"].tolist() == [15, 25, 0, 0, 0, 0, 0]


# Test for calculate_average_people_in_line_by_bucket
def test_calculate_average_people_in_line_by_bucket():
    data = pd.DataFrame(
        {
            "avg_num_wait_queue_Nq": [2, 4, 6, 8, 10, 12],
            "type_of_checkout": [
                "self",
                "self",
                "self",
                "self",
                "self",
                "self",
            ],
        }
    )
    result = calculate_average_people_in_line_by_bucket(data)
    assert "self" in result.columns
    assert result["self"].tolist() == [0, 2, 4, 6, 8, 10, 12]


# Test for calculate_average_wait_time_by_hour
def test_calculate_average_wait_time_by_hour():
    data = pd.DataFrame(
        {
            "hour": [9, 10],
            "type_of_checkout": ["self", "self"],
            "avg_waiting_time_Tq": [5, 15],
        }
    )
    result = calculate_average_wait_time_by_hour(data)
    assert "self" in result.columns
    assert result["self"].tolist() == [5, 15]


# Test for calculate_wait_time_vs_queue_length
def test_calculate_wait_time_vs_queue_length():
    data = pd.DataFrame(
        {
            "hour": [9, 10],
            "type_of_checkout": ["self", "self"],
            "avg_waiting_time_Tq": [5, 15],
            "avg_num_wait_queue_Nq": [10, 20],
        }
    )
    result = calculate_wait_time_vs_queue_length(data)
    assert "avg_wait_time" in result.columns
    assert "avg_queue_length" in result.columns
    assert result["avg_wait_time"]["self"].tolist() == [5, 15]
    assert result["avg_queue_length"]["self"].tolist() == [10, 20]


# Test for extract_unique_lane_types
def test_extract_unique_lane_types():
    data = pd.DataFrame(
        {
            "type_of_checkout": ["self", "manned", "self", "manned"],
        }
    )
    result = extract_unique_lane_types(data)
    assert set(result) == {"self", "manned"}


# Test for get_lane_type_values
def test_get_lane_type_values():
    class TestLaneType(Enum):
        value_1 = "test_1"
        value_2 = "test_2"

    lane_types = [
        LaneType.MANNED_TRADITIONAL,
        LaneType.REVERSIBLE_MCO_TRADITIONAL_EXPRESS,
    ]
    result = get_lane_type_values(lane_types)
    assert result == [
        LaneType.MANNED_TRADITIONAL.value,
        LaneType.REVERSIBLE_MCO_TRADITIONAL_EXPRESS.value,
    ]


# Test for get_history_df with EmptyDataError
@patch("backend.src.app.services.core.review_k_p_i.CONFIGS", {})
@pytest.mark.asyncio
async def test_get_history_df_no_data():
    with pytest.raises(EmptyDataError, match="No data found"):
        await get_history_df()


# Test for get_history_df with valid data
@patch(
    "backend.src.app.services.core.review_k_p_i.CONFIGS",
    {"HISTORICAL_DATA_FRAME": pd.DataFrame({"col1": [1, 2]})},
)
@pytest.mark.asyncio
async def test_get_history_df_with_data():
    result = await get_history_df()
    assert isinstance(result, pd.DataFrame)
    assert "col1" in result.columns
    assert result["col1"].tolist() == [1, 2]


# Test for get_wait_time with empty DataFrame
@pytest.mark.asyncio
async def test_get_wait_time_empty_df():
    with pytest.raises(
        EmptyDataError, match="No data found for the given filters"
    ):
        await process_metric_calculation_and_format_into_split(pd.DataFrame())


# Test for process_review_k_p_i
@pytest.mark.asyncio
async def test_process_review_k_p_i_function_calls():
    # Create a Params instance with default values
    params = Params()

    # Mock data to simulate the DataFrame
    mock_data = pd.DataFrame(
        {
            "hour": [9, 10],
            "type_of_checkout": ["self", "self"],
            "avg_waiting_time_Tq": [5, 15],
            "avg_num_wait_queue_Nq": [10, 20],
            "weekday_name": ["Monday", "Tuesday"],
            "Wait_Time_BKT": [" 0 - 30 sec", "30 sec - 1 min"],
            "new_clusters": [1, 1],
            "store_name": [16, 29],
            "peak_hour": [0, 1],
            "Covid_Effect": [0, 0],
            "event": ["Event1", "Event2"],
            "date": pd.to_datetime(["2023-10-01", "2023-10-02"]),
        }
    )

    # Patch the functions to mock their behavior
    with patch(
        "backend.src.app.services.core.review_k_p_i.get_history_df",
        return_value=mock_data,
    ) as mock_get_df, patch(
        "backend.src.app.services.core.review_k_p_i.filter_df",
        return_value=mock_data,
    ) as mock_filter_df, patch(
        "backend.src.app.services.core.review_k_p_i.get_wait_time",
        return_value={"dummy_key": "dummy_value"},
    ) as mock_performance_function:

        # Call the process_review_k_p_i function with the params
        result = await process_review_k_p_i(params)

        # Assert that the get_history_df function was called once
        mock_get_df.assert_called_once()

        # Assert that the filter_df function was called once with the correct arguments
        mock_filter_df.assert_called_once_with(
            kpi_data=mock_data, params=params
        )

        # Assert that the performance function was called once with the correct arguments
        mock_performance_function.assert_called_once_with(
            filtered_df=mock_data
        )

        # Assert that the result is as expected
        assert result == {"dummy_key": "dummy_value"}


@pytest.mark.asyncio
async def test_process_review_k_p_i_success():
    # Mock the inner functions to ensure they are called
    mock_performance_type_function = AsyncMock()
    mock_get_df_func = AsyncMock()
    mock_filter_df = AsyncMock()

    with patch.dict(
        (
            "backend.src.app.services.core.review_k_p_i.performance_type_functions_map"
        ),
        {"some_type": mock_performance_type_function},
    ), patch.dict(
        "backend.src.app.services.core.review_k_p_i.data_form_get_df_map",
        {"some_data_form": mock_get_df_func},
    ), patch.object(
        "backend.src.app.services.core.review_k_p_i",
        "filter_df",
        mock_filter_df,
    ):

        params = Params(
            type="some_type", data_form="some_data_form"
        )  # Replace with actual Params object

        await process_review_k_p_i(params)

        # Assert that all inner functions were called
        mock_get_df_func.assert_awaited_once()
        mock_filter_df.assert_awaited_once()
        mock_performance_type_function.assert_awaited_once()
