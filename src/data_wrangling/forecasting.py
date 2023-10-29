from src.data_wrangling.dict_transformations import reduce_dict_by_time
from src.data_wrangling.dict_transformations import sort_dict_by_time


def forecast(source_dict: dict, until: str, method: str = "mean", **kwargs) -> dict:
    """Forecast future incomes or expenses
    ----------
    Parameters:
    source_dict : dictionary with incomes-expenses data
    until : date until which data was recorded (inclusivly)
    method : method used for forcast, "mean" by default
    **kwargs : keyword arguments to pass for inner method functions
    -------
    Returns:
    dictionary with forcasted data
    """

    def mean(source_dict: dict, until: str, **kwargs) -> dict:
        """Forecast by mean values of previous periods
        ----------
        Parameters:
        source_dict : dictionary with incomes-expenses data
        until : date until which data was recorded (inclusivly)
        **kwargs : just for compatability
        -------
        Returns:
        dictionary with forcasted data
        """
        forecasted_dict = {}
        stop_summirize = False
        mean = 0
        for i, (key, value) in enumerate(source_dict.items()):
            if not stop_summirize:
                forecasted_dict[key] = value.values.sum()
                if key == until:
                    sum = 0
                    for summand in forecasted_dict.values():
                        sum += summand
                    mean = sum / (i + 1)
                    mean = round(mean)
                    stop_summirize = True
            else:
                forecasted_dict[key] = mean
        return forecasted_dict

    def drop_channels(source_dict: dict, until: str, channels: list, **kwargs) -> dict:
        """Forecast by mean values of previous periods but drop some income or expense channels
        ----------
        Parameters:
        source_dict : dictionary with incomes-expenses data
        until : date until which data was recorded (inclusivly)
        channels : list with column names to drop from calculations of the mean
        **kwargs : just for compatability
        -------
        Returns:
        dictionary with forcasted data
        """
        edited_dict = source_dict.copy()
        for key in source_dict.keys():
            for channel in channels:
                if channel in source_dict[key].columns:
                    edited_dict[key] = edited_dict[key].drop(channel, axis="columns")
        forecasted_dict = mean(edited_dict, until)
        return forecasted_dict

    source_dict = sort_dict_by_time(source_dict)
    forecasted_dict = eval(f"{method}(source_dict, until, **kwargs)")
    return forecasted_dict


def forecast_savings(
    source_dict: dict,
    incomes_dict: dict,
    expenses_dict: dict,
    until: str,
) -> dict:
    """Forecast future savings
    ----------
    Parameters:
    source_dict : dictionary with savings data
    incomes_dict : dictionary with incomes data
    expenses_dict : dictionary with expenses data
    until : date until which data was recorded (inclusivly)
    -------
    Returns:
    dictionary with forcasted data
    """
    source_dict = sort_dict_by_time(source_dict)
    incomes_dict = sort_dict_by_time(incomes_dict)
    expenses_dict = sort_dict_by_time(expenses_dict)
    forecasted_dict = {}
    start_sum_savings = False
    save_value = 0
    for key, value in source_dict.items():
        if not start_sum_savings:
            forecasted_dict[key] = source_dict[key].iat[-1]
            if key == until:
                save_value = value.iat[-1]
                start_sum_savings = True
        else:
            forecasted_dict[key] = incomes_dict[key] - expenses_dict[key] + save_value
            save_value = forecasted_dict[key]
    return forecasted_dict
