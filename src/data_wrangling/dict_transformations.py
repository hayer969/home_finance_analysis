from datetime import datetime


def sort_dict_by_time(source_dict: dict, ascending: bool = True) -> dict:
    """Sort dictionary by key by time
    ----------
    Parameters:
    source_dict : dictionary with keys in format Month_Year
    ascending : sort order
    -------
    Returns:
    sorted dictionary
    """
    ru_to_eng_months = {
        "Январь": "January",
        "Февраль": "February",
        "Март": "March",
        "Апрель": "April",
        "Май": "May",
        "Июнь": "June",
        "Июль": "July",
        "Август": "August",
        "Сентябрь": "September",
        "Октябрь": "October",
        "Ноябрь": "November",
        "Декабрь": "December",
    }
    keys = []
    for key in source_dict.keys():
        for ru_month, eng_month in ru_to_eng_months.items():
            key = key.lower().capitalize()
            key = key.replace(ru_month, eng_month)
        key = datetime.strptime(key, "%B_%Y")
        keys.append(key)
    time_dict = dict(zip(keys, list(source_dict.values())))
    sorted_time_dict = dict(sorted(time_dict.items(), reverse=(not ascending)))
    keys = []
    for key in sorted_time_dict.keys():
        key = key.strftime("%B_%Y")
        for ru_month, eng_month in ru_to_eng_months.items():
            key = key.replace(eng_month, ru_month)
        keys.append(key)
    sorted_dict = dict(zip(keys, list(sorted_time_dict.values())))
    return sorted_dict


def reduce_dict_by_time(
    source_dict: dict, start_month: str, end_month: str = False
) -> dict:
    """Reduce dictionary by key by time, stay only period of an interest
    ----------
    Parameters:
    source_dict : dictionary with keys in format Month_Year
    start_month : dictionary key from which final dictionary starts
    end_month : dictionary key until which final dictionary ends
    -------
    Returns:
    reduced dictionary
    """

    def del_items(sdict: dict, keys: list, month: str):
        for key in keys:
            if key == month:
                break
            del sdict[key]
        return sdict

    source_dict = sort_dict_by_time(source_dict)
    start_keys = list(source_dict.keys())
    source_dict = del_items(source_dict, start_keys, start_month)
    if end_month:
        end_keys = list(source_dict.keys())
        end_keys.reverse()
        source_dict = del_items(source_dict, end_keys, end_month)
    return source_dict
