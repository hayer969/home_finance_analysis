import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from src.data_wrangling.dict_transformations import sort_dict_by_time


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


def plot_alluvial(inp_dict: dict) -> None:
    """Plot alluvial chart from yearly spends or incomes groups to monthes
    ----------
    Parameters:
    inp_dict : dictionary with data, such as monthly expenses
    -------
    Returns:
    picture from plotly
    """
    groups = [group.index.tolist() for group in inp_dict.values()]
    groups = [group for sublist in groups for group in sublist]
    groups = list(set(groups))
    groups = sorted(groups)
    columns = ["groups", "time", "values"]
    df = pd.DataFrame(columns=columns)
    for key, values in inp_dict.items():
        for group, value in values.items():
            row = pd.DataFrame(data=[[group, key, value]], columns=columns)
            df = pd.concat([df, row])
    df = df.fillna(0)

    inp_dict = sort_dict_by_time(inp_dict)
    monthes = list(inp_dict.keys())
    labels = groups + monthes
    color = "papayawhip"
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(label=labels, color=color),
                link=dict(
                    source=[
                        labels.index(group)
                        for idx, group in enumerate(df["groups"])
                        if df["values"].iloc[idx] > 0
                    ],
                    target=[
                        labels.index(time)
                        for idx, time in enumerate(df["time"])
                        if df["values"].iloc[idx] > 0
                    ],
                    value=[
                        value
                        for idx, value in enumerate(df["values"])
                        if df["values"].iloc[idx] > 0
                    ],
                    color=color,
                ),
            )
        ]
    )
    fig.update_layout()
    fig.show()
