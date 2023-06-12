# %%
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objects as go


def prepare_data(filename: str, drop: list, food_consume: bool = False) -> pd.DataFrame:
    """Load sheets from excel file
    ----------
    Parameters:
    filename : filename of the excel file (str)
    drop : names of sheets to drop
    food_consume : does this file contains food consuming info
    -------
    Returns:
    pd_sheets : pandas DataFrames
    """
    workbook = pd.read_excel(
        filename,
        sheet_name=None,
        nrows=31,
        skiprows=2,
        header=None,
    )
    workbook_columns = pd.read_excel(
        filename,
        sheet_name=None,
        nrows=2,
        header=None,
    )
    for sheet in drop:
        workbook.pop(sheet)
        workbook_columns.pop(sheet)

    for key, sheet_column in workbook_columns.items():
        sheet_column = sheet_column.ffill().ffill(axis="columns")
        sheet_column = sheet_column.transpose()
        workbook[key].columns = pd.MultiIndex.from_frame(sheet_column)
        workbook[key] = workbook[key].dropna(subset=[("дата", "дата")])
        workbook[key] = workbook[key].set_index([("дата", "дата")])

    workbook_incomes = {key: value["доход"] for (key, value) in workbook.items()}
    for key in workbook_incomes.keys():
        workbook_incomes[key] = workbook_incomes[key].drop(
            "общ. приход", axis="columns"
        )
        workbook_incomes[key] = workbook_incomes[key].fillna(0)

    workbook_savings = {
        key: value.xs("остаток", level=1, axis="columns", drop_level=False)
        for (key, value) in workbook.items()
    }
    for key in workbook_savings.keys():
        workbook_savings[key] = (
            workbook_savings[key].droplevel(0, axis="columns").squeeze()
        )
        workbook_savings[key] = workbook_savings[key].fillna(0)

    workbook_expenses = {}
    for key in workbook.keys():
        idx = workbook[key].columns.get_level_values(1).tolist().index("остаток")
        workbook_expenses[key] = workbook[key].iloc[:, idx + 1 :]
        workbook_expenses[key] = workbook_expenses[key].fillna(0)

    food_consuming = {}
    if food_consume:
        food_consuming = pd.read_excel(
            filename,
            sheet_name=None,
            nrows=1,
            skiprows=34,
            usecols="J:O",
            index_col=0,
            header=None,
        )
        for sheet in drop:
            food_consuming.pop(sheet)

        for key in food_consuming.keys():
            food_consuming[key] = food_consuming[key].squeeze("columns")
            food_consuming[key] = food_consuming[key].transpose()
            food_consuming[key].index = (
                workbook_expenses[key]["еда"].columns.get_level_values(0).tolist()[:5]
            )
            food_consuming[key] = food_consuming[key].fillna(0)

    return workbook_incomes, workbook_savings, workbook_expenses, food_consuming


def plot_margin_matplotlib(
    inc_dict: dict, savings_dict: dict, expenses_dict: dict
) -> None:
    """Plot margin bar chart
    ----------
    Parameters:
    inc_dict : dictionary with monthly incomes
    savings_dict : dictionary with monthly savings
    expenses_dict : dictionary with monthly expenses
    -------
    Returns:
    picture from matplotlib
    """
    chart_margin = pd.DataFrame()
    chart_margin["Доходы"] = pd.Series(inc_dict)
    chart_margin["Расходы"] = pd.Series(expenses_dict)
    chart_margin["Прибыль"] = chart_margin["Доходы"] - chart_margin["Расходы"]
    chart_margin["Накопления"] = pd.Series(savings_dict)
    mask = chart_margin.copy()
    for i in range(len(mask.columns)):
        mask.iloc[:, i] = i + 1
    mask = mask.transpose()
    mask = mask.to_numpy().flatten()

    plt.rcParams.update({"figure.autolayout": True})
    ax = chart_margin.plot(kind="bar", position=0.5)
    ax.set_xticklabels(chart_margin.index.tolist(), rotation=270)
    color = ["#3d85c6", "#ff0000", "#8fce00", "#fff7c4"]

    for i, p in enumerate(ax.patches):
        text = str(p.get_height()) if p.get_height() != 0 else ""
        if mask[i] == 4:
            ax.annotate(text, (p.get_x(), p.get_height() * 1.05))
            plt.setp(
                p,
                width=0.9,
                zorder=1,
                x=p.get_x() - 0.5,
                color=color[mask[i] - 1],
            )
        else:
            distance = p.get_x() + 0.1 * mask[i] - 0.1
            abs_height = abs(p.get_height())
            height = (
                p.get_height() * (1 + mask[i] * 0.1)
                if abs_height < 100000
                else p.get_height()
            )
            ax.annotate(text, (distance, height))
            plt.setp(p, width=0.2, zorder=2, x=distance, color=color[mask[i] - 1])

    ax.legend()
    ax.axhline(y=0.0)
    plt.show()


def plot_margin(inc_dict: dict, savings_dict: dict, expenses_dict: dict) -> None:
    """Plot margin bar chart
    ----------
    Parameters:
    inc_dict : dictionary with monthly incomes
    savings_dict : dictionary with monthly savings
    expenses_dict : dictionary with monthly expenses
    -------
    Returns:
    picture from plotly
    """
    chart_margin = pd.DataFrame()
    chart_margin["Доходы"] = pd.Series(inc_dict)
    chart_margin["Расходы"] = pd.Series(expenses_dict)
    chart_margin["Прибыль"] = chart_margin["Доходы"] - chart_margin["Расходы"]
    chart_margin["Накопления"] = pd.Series(savings_dict)
    colors = [
        "#3d85c6",
        "#ff0000",
        "#ffff00",
        "#ffffcd",
    ]

    layout = go.Layout(
        xaxis=dict(overlaying="x2"),
        xaxis2=dict(
            title="Накопления",
            side="top",
            tickmode="array",
            tickvals=chart_margin.index.tolist(),
            ticktext=chart_margin["Накопления"],
        ),
    )
    fig = go.Figure(layout=layout)
    for coloridx, key in enumerate(chart_margin.columns[:3]):
        fig.add_trace(
            go.Bar(
                x=chart_margin.index.tolist(),
                y=chart_margin[key],
                text=chart_margin[key],
                opacity=0.85,
                marker_color=[colors[coloridx] for _ in range(len(chart_margin.index))],
                name=key,
            )
        )
    fig.add_trace(
        go.Bar(
            x=chart_margin.index.tolist(),
            y=chart_margin["Накопления"],
            xaxis="x2",
            width=0.9,
            offset=-0.45,
            cliponaxis=False,
            marker_color=[colors[3] for _ in range(len(chart_margin.index))],
            name="Накопления",
        )
    )
    fig.update_layout(barmode="group", yaxis=dict(title="RUB (тысячи)"))
    fig.show()


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


# %%
my_2021 = "./data/incomes-expenses_2021.xlsx"
my_2022 = "./data/incomes-expenses_2022.xlsx"
my_2023 = "./data/incomes-expenses_2023.xlsx"
inc21, sav21, exp21, _ = prepare_data(
    my_2021, drop=["Декабрь_2020", "Отчет"], food_consume=False
)
inc22, sav22, exp22, _ = prepare_data(
    my_2022, drop=["Декабрь_2021", "Отчет"], food_consume=False
)
inc23, sav23, exp23, food_cons23 = prepare_data(
    my_2023, drop=["Декабрь_2022"], food_consume=True
)
# %%
# Прибыль за год
incomes = {**inc21, **inc22, **inc23}
savings = {**sav21, **sav22, **sav23}
expenses = {**exp21, **exp22, **exp23}
# incomes = reduce_dict_by_time(incomes, "Май_2023")

finc = forecast(incomes, until="Май_2023")
fexpenses = forecast(
    expenses,
    until="Июнь_2023",
    # method="drop_channels",
    # channels=[("семейные", "отдых"), ("Отдых", "Путешествия")],
)
fsavings = forecast_savings(savings, finc, fexpenses, until="Июнь_2023")

finc = reduce_dict_by_time(finc, "Январь_2023")
fexpenses = reduce_dict_by_time(fexpenses, "Январь_2023")
fsavings = reduce_dict_by_time(fsavings, "Январь_2023")

plot_margin(finc, fsavings, fexpenses)
# %%
# Доход за год по группам
inc_sum_dict = {key: value.sum() for (key, value) in incomes.items()}
chart_incomes = pd.DataFrame(inc_sum_dict)
chart_incomes = chart_incomes.transpose()
chart_incomes["итого"] = chart_incomes.sum("columns")
mask = chart_incomes.copy()
mask.loc[:, :] = False
mask["итого"] = True
mask = mask.transpose()
mask = mask.to_numpy().flatten()

plt.rcParams.update({"figure.autolayout": True})
ax = chart_incomes.plot(kind="bar", position=0.5)
ax.set_xticklabels(chart_incomes.index.tolist(), rotation=270)

for i, p in enumerate(ax.patches):
    text = str(p.get_height()) if p.get_height() != 0 else ""
    if mask[i]:
        ax.annotate(text, (p.get_x(), p.get_height() * 1.05))
        plt.setp(
            p,
            width=0.9,
            zorder=1,
            x=p.get_x() - 0.5,
            color="#fff7c4",
        )
    else:
        ax.annotate(text, (p.get_x() - 0.025, p.get_height() * 0.9))
        plt.setp(p, width=0.2, zorder=2)

ax.legend()
plt.show()
# %%
