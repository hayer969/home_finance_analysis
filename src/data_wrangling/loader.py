import pandas as pd


def prepare_data(
    filename: str, drop: list[str] = [], food_consume: bool = False
) -> pd.DataFrame:
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
    workbook = dict((k.capitalize().replace(" ", "_"), v) for k, v in workbook.items())
    workbook_columns = dict(
        (k.capitalize().replace(" ", "_"), v) for k, v in workbook_columns.items()
    )
    for sheet in drop:
        sheet = sheet.capitalize().replace(" ", "_")
        workbook.pop(sheet)
        workbook_columns.pop(sheet)

    for key, sheet_column in workbook_columns.items():
        sheet_column = sheet_column.ffill().ffill(axis="columns")
        sheet_column = sheet_column.transpose()
        workbook[key].columns = pd.MultiIndex.from_frame(sheet_column)
        workbook[key] = workbook[key].dropna(subset=[("дата", "дата")])
        workbook[key] = workbook[key].set_index(keys=("дата", "дата"))

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
