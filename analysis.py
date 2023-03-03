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
        nrows=30,
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
    for key, sheet in workbook_incomes.items():
        workbook_incomes[key] = sheet.drop("общ. приход", axis="columns")
    workbook_savings = {
        key: value.xs("остаток", level=1, axis="columns", drop_level=False)
        for (key, value) in workbook.items()
    }

    for key, sheet in workbook_savings.items():
        workbook_savings[key] = sheet.droplevel(0, axis="columns").squeeze()

    workbook_expenses = {}
    for key, sheet in workbook.items():
        idx = sheet.columns.get_level_values(1).tolist().index("остаток")
        workbook_expenses[key] = sheet.iloc[:, idx + 1 :]

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

    for key, sheet in food_consuming.items():
        food_consuming[key] = sheet.squeeze("columns")
        food_consuming[key] = food_consuming[key].transpose()
        food_consuming[key].index = (
            workbook_expenses[key]["еда"].columns.get_level_values(0).tolist()[:5]
        )

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
ch_in_x = chart_incomes.plot(kind="bar", width=1.5, position=0)
ch_in_x.set_xticklabels(chart_incomes.index.tolist(), rotation=270)
for p in ch_in_x.patches:
    ch_in_x.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
plt.show()
# %%
