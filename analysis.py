# %%
from numpy import char, squeeze
import pandas as pd
import matplotlib.pyplot as plt
from pandas.core.interchange.dataframe_protocol import enum


def prepare_data(filename: str) -> pd.DataFrame:
    """Load sheets from excel file
    ----------
    Parameters:
    filename : filename of the excel file (str)
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

    food_consuming = pd.read_excel(
        filename,
        sheet_name=None,
        nrows=1,
        skiprows=34,
        usecols="J:O",
        index_col=0,
        header=None,
    )
    # Не подходит по названиям, это исключение
    food_consuming.pop("Декабрь_2022")

    for key in food_consuming.keys():
        food_consuming[key] = food_consuming[key].squeeze("columns")
        food_consuming[key] = food_consuming[key].transpose()
        food_consuming[key].index = (
            workbook_expenses[key]["еда"].columns.get_level_values(0).tolist()[:5]
        )
        food_consuming[key] = food_consuming[key].fillna(0)

    return workbook_incomes, workbook_savings, workbook_expenses, food_consuming


my_2023 = "./data/incomes-expenses_2023.xlsx"
incomes, savings, expenses, food_consuming = prepare_data(my_2023)
incomes.pop("Декабрь_2022")
savings.pop("Декабрь_2022")
expenses.pop("Декабрь_2022")
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
# Прибыль за год
inc_dict = {key: value.values.sum() for (key, value) in incomes.items()}
savings_dict = {key: value.iat[-1] for (key, value) in savings.items()}
expenses_dict = {key: value.values.sum() for (key, value) in expenses.items()}

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

for i, p in enumerate(ax.patches):
    text = str(p.get_height()) if p.get_height() != 0 else ""
    ax.annotate(text, (p.get_x(), p.get_height() * 1.05))
    if mask[i] == 4:
        plt.setp(
            p,
            width=0.9,
            zorder=1,
            x=p.get_x() - 0.5,
            color="#fff7c4",
        )
    else:
        distance = p.get_x() + 0.1 * mask[i] - 0.1
        plt.setp(p, width=0.2, zorder=2, x=distance)

ax.legend()
plt.show()
# %%
