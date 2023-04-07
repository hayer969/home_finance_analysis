# %%
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


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


def plot_margin(inc_dict: dict, savings_dict: dict, expenses_dict: dict) -> None:
    """Plot margin bar chart
    ----------
    Parameters:
    inc_dict: dictionary with monthly incomes
    savings_dict: dictionary with monthly savings
    expenses_dict: dictionary with monthly expenses
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
            height = p.get_height() * 1.1
            ax.annotate(text, (distance, height))
            plt.setp(p, width=0.2, zorder=2, x=distance, color=color[mask[i] - 1])

    ax.legend()
    ax.axhline(y=0.0)
    plt.show()


def sort_dict_by_time(source_dict: dict, ascending: bool = True) -> dict:
    """Sort dictionary by key by time
    ----------
    Parameters:
    source_dict: dictionary with keys in format Month_Year
    ascending: sort order
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
incomes = {**inc21, **inc22, **inc23}
savings = {**sav21, **sav22, **sav23}
expenses = {**exp21, **exp22, **exp23}
incomes = sort_dict_by_time(incomes)
savings = sort_dict_by_time(savings)
expenses = sort_dict_by_time(expenses)
# %%
# Прибыль за год
inc_dict = {key: value.values.sum() for (key, value) in incomes.items()}
savings_dict = {key: value.iat[-1] for (key, value) in savings.items()}
expenses_dict = {key: value.values.sum() for (key, value) in expenses.items()}

plot_margin(inc_dict, savings_dict, expenses_dict)
# %%
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
