from src.data_wrangling.loader import prepare_data
from src.data_wrangling.dict_transformations import reduce_dict_by_time
from src.data_wrangling.forecasting import forecast
from src.data_wrangling.forecasting import forecast_savings
from src.data_wrangling.plotting import plot_margin


def main() -> int:
    my_2012 = "./data/incomes-expenses_2012.xlsx"
    my_2013 = "./data/incomes-expenses_2013.xlsx"
    my_2014 = "./data/incomes-expenses_2014.xlsx"
    my_2015 = "./data/incomes-expenses_2015.xlsx"
    my_2016 = "./data/incomes-expenses_2016.xlsx"
    my_2017 = "./data/incomes-expenses_2017.xlsx"
    my_2018 = "./data/incomes-expenses_2018.xlsx"
    my_2019 = "./data/incomes-expenses_2019.xlsx"
    my_2020 = "./data/incomes-expenses_2020.xlsx"
    my_2021 = "./data/incomes-expenses_2021.xlsx"
    my_2022 = "./data/incomes-expenses_2022.xlsx"
    my_2023 = "./data/incomes-expenses_2023.xlsx"
    inc12, sav12, exp12, _ = prepare_data(
        my_2012,
        drop=["Декабрь_2011", "Октябрь_2011", "Ноябрь_2011"],
        food_consume=False,
    )
    inc13, sav13, exp13, _ = prepare_data(
        my_2013, drop=["Декабрь_2012"], food_consume=False
    )
    inc14, sav14, exp14, _ = prepare_data(
        my_2014, drop=["Декабрь_2013"], food_consume=False
    )
    inc15, sav15, exp15, _ = prepare_data(
        my_2015, drop=["Декабрь_2014"], food_consume=False
    )
    inc16, sav16, exp16, _ = prepare_data(my_2016, food_consume=False)
    inc17, sav17, exp17, _ = prepare_data(
        my_2017, drop=["Декабрь_2016"], food_consume=False
    )
    inc18, sav18, exp18, _ = prepare_data(
        my_2018, drop=["Декабрь_2017"], food_consume=False
    )
    inc19, sav19, exp19, _ = prepare_data(
        my_2019, drop=["Декабрь_2018"], food_consume=False
    )
    inc20, sav20, exp20, _ = prepare_data(
        my_2020, drop=["Декабрь_2019"], food_consume=False
    )
    inc21, sav21, exp21, _ = prepare_data(
        my_2021, drop=["Декабрь_2020", "Отчет"], food_consume=False
    )
    inc22, sav22, exp22, _ = prepare_data(
        my_2022, drop=["Декабрь_2021", "Отчет"], food_consume=False
    )
    inc23, sav23, exp23, food_cons23 = prepare_data(
        my_2023, drop=["Декабрь_2022"], food_consume=True
    )
    # Прибыль за год
    incomes = {
        **inc12,
        **inc13,
        **inc14,
        **inc15,
        **inc16,
        **inc17,
        **inc18,
        **inc19,
        **inc20,
        **inc21,
        **inc22,
        **inc23,
    }
    savings = {
        **sav12,
        **sav13,
        **sav14,
        **sav15,
        **sav16,
        **sav17,
        **sav18,
        **sav19,
        **sav20,
        **sav21,
        **sav22,
        **sav23,
    }
    expenses = {
        **exp12,
        **exp13,
        **exp14,
        **exp15,
        **exp16,
        **exp17,
        **exp18,
        **exp19,
        **exp20,
        **exp21,
        **exp22,
        **exp23,
    }
    # incomes = reduce_dict_by_time(incomes, "Сентябрь_2023")

    finc = forecast(incomes, until="Октябрь_2023")
    fexpenses = forecast(
        expenses,
        until="Октябрь_2023",
        # method="drop_channels",
        # channels=[("семейные", "отдых"), ("Отдых", "Путешествия")],
    )
    fsavings = forecast_savings(savings, finc, fexpenses, until="Октябрь_2023")

    finc = reduce_dict_by_time(finc, start_month="Январь_2023")
    fexpenses = reduce_dict_by_time(fexpenses, start_month="Январь_2023")
    fsavings = reduce_dict_by_time(fsavings, start_month="Январь_2023")

    plot_margin(finc, fsavings, fexpenses)
    # # %%
    #     exp_sum_dict = {key: value.sum() for (key, value) in expenses.items()}
    #     exp_sum_dict = reduce_dict_by_time(exp_sum_dict, "Январь_2023")
    #     plot_alluvial(exp_sum_dict)
    # # %%
    # # Доход за год по группам
    #     inc_sum_dict = {key: value.sum() for (key, value) in incomes.items()}
    #     chart_incomes = pd.DataFrame(inc_sum_dict)
    #     chart_incomes = chart_incomes.transpose()
    #     chart_incomes["итого"] = chart_incomes.sum("columns")
    #     mask = chart_incomes.copy()
    #     mask.loc[:, :] = False
    #     mask["итого"] = True
    #     mask = mask.transpose()
    #     mask = mask.to_numpy().flatten()
    #
    #     plt.rcParams.update({"figure.autolayout": True})
    #     ax = chart_incomes.plot(kind="bar", position=0.5)
    #     ax.set_xticklabels(chart_incomes.index.tolist(), rotation=270)
    #
    #     for i, p in enumerate(ax.patches):
    #         text = str(p.get_height()) if p.get_height() != 0 else ""
    #         if mask[i]:
    #             ax.annotate(text, (p.get_x(), p.get_height() * 1.05))
    #             plt.setp(
    #                 p,
    #                 width=0.9,
    #                 zorder=1,
    #                 x=p.get_x() - 0.5,
    #                 color="#fff7c4",
    #             )
    #         else:
    #             ax.annotate(text, (p.get_x() - 0.025, p.get_height() * 0.9))
    #             plt.setp(p, width=0.2, zorder=2)
    #
    #     ax.legend()
    # plt.show()
    return 0


if __name__ == "__main__":
    exit(main())
