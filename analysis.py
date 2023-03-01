# %%
import pandas as pd

workbook = pd.read_excel(
    "./data/incomes-expenses_2023.xlsx",
    sheet_name=None,
    nrows=30,
    skiprows=2,
    header=None,
)
# %%
workbook_columns = pd.read_excel(
    "./data/incomes-expenses_2023.xlsx",
    sheet_name=None,
    nrows=2,
    header=None,
)

for sheet_column, sheet in zip(workbook_columns.values(), workbook.values()):
    sheet_column = sheet_column.ffill(axis="columns").ffill()
    sheet_column = sheet_column.transpose()
    sheet.columns = pd.MultiIndex.from_frame(sheet_column)
    sheet.dropna(inplace=True)
    sheet.set_index([("дата", "дата")], inplace=True)
# %%
