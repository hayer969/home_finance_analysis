# %%
import pandas as pd
import matplotlib.pyplot as plt

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
    sheet_column = sheet_column.ffill().ffill(axis="columns")
    sheet_column = sheet_column.transpose()
    sheet.columns = pd.MultiIndex.from_frame(sheet_column)
    sheet.dropna(subset=[("дата", "дата")], inplace=True)
    sheet.set_index([("дата", "дата")], inplace=True)
# %%
workbook_incomes = {key: value["доход"] for (key, value) in workbook.items()}
for key, sheet in workbook_incomes.items():
    workbook_incomes[key] = sheet.drop("общ. приход", axis="columns")
# %%
workbook_savings = {
    key: value.xs("остаток", level=1, axis="columns", drop_level=False)
    for (key, value) in workbook.items()
}
for key, sheet in workbook_savings.items():
    workbook_savings[key] = sheet.droplevel(0, axis="columns").squeeze()
# %%
workbook_expenses = {}
for key, sheet in workbook.items():
    idx = sheet.columns.get_level_values(1).tolist().index("остаток")
    workbook_expenses[key] = sheet.iloc[:, idx + 1:]
# %%
ax = workbook_incomes["Февраль_2023"].plot(kind="bar", width=5.0)
ax.set_xticklabels(
    [x.strftime("%d-%m-%y") for x in workbook_incomes["Февраль_2023"].index],
    rotation=45,
)
plt.show()
# %%
workbook_incomes["Февраль_2023"]["Sum up"] = (
    workbook_incomes["Февраль_2023"].sum(axis="columns").squeeze()
)
# %%
