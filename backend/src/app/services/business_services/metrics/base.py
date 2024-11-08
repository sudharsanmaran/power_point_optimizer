import numpy as np


def calculate_average(data, group_by_cols, target_col, index_labels):
    """Helper function to calculate the average and reindex."""
    pivot_data = data.groupby(group_by_cols)[[target_col]].mean().unstack()
    pivot_data.columns = pivot_data.columns.get_level_values(1)
    pivot_data.reset_index(inplace=True)
    pivot_data = pivot_data.set_index(group_by_cols[0])
    pivot_data = pivot_data.reindex(index_labels, fill_value=0).reset_index()
    return pivot_data.replace(np.nan, 0)
