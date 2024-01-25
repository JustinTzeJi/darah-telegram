import os
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/creds.json"


def read_sql(sql_path):
    with open(sql_path, "r") as f:
        query = f.read()
    return query


def malaysia_cumulative_analytics():
    malaysia_cumulative_query = read_sql("sql/malaysia_total.sql")
    malaysia_cumulative = pd.read_gbq(
        query=malaysia_cumulative_query, project_id="articulate-case-410317"
    )
    actual = malaysia_cumulative[~malaysia_cumulative.daily.isna()]
    if (
        actual.cumulative_daily_donations.iat[-1]
        > actual.cumulative_daily_donations_prev_year.iat[-1]
    ):
        colour = "green"
    else:
        colour = "red"
    ytd_growth = (
        actual.cumulative_daily_donations.iat[-1]
        - actual.cumulative_daily_donations_prev_year.iat[-1]
    ) / actual.cumulative_daily_donations_prev_year.iat[-1]

    if ytd_growth > 0:
        emoji = "🟢"
    else:
        emoji = "🔴"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=malaysia_cumulative["date"],
            y=malaysia_cumulative["cumulative_daily_donations_prev_year"],
            name="2023",
            line=dict(color="grey", dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=malaysia_cumulative["date"],
            y=malaysia_cumulative["cumulative_daily_donations"],
            name="2024",
            mode="lines+markers",
            line=dict(color=colour),
        )
    )
    fig.add_annotation(
        x=actual["date"].iat[-1],
        y=actual["cumulative_daily_donations_prev_year"].iat[-1],
        text=f'2023 cumulative daily donations: {actual["cumulative_daily_donations_prev_year"].iat[-1]}',
        showarrow=True,
        ax=0,
        ay=70,
        arrowhead=5,
        arrowcolor="grey",
    )

    fig.add_annotation(
        x=actual["date"].iat[-1],
        y=actual["cumulative_daily_donations"].iat[-1],
        text=f'2024 cumulative daily donations: {actual["cumulative_daily_donations"].iat[-1]}',
        showarrow=True,
        arrowcolor="black",
        ax=0,
        ay=-50,
        arrowhead=0,
    )
    fig.update_layout(
        title="YTD cumulative blood donations",
        xaxis_title="Date",
        yaxis_title="Blood Donations",
    )
    fig.write_image("malaysia_cumulative.png", width=1200, height=500)

    message = f"""Total Daily Donations ({actual["date"].iat[-1]}): {actual["daily"].iat[-1]}
	Year-to-date cumulative donations growth (vs {actual["date"].iat[-1] - relativedelta(years=1)}: ytd_growth {emoji}
	"""
    return message


def state_cumulative_analytics():
    state_cumulative_query = read_sql("sql/state_total.sql")
    state_cumulative = pd.read_gbq(
        query=state_cumulative_query, project_id="articulate-case-410317"
    )
    states = state_cumulative.state.unique()
    fig = make_subplots(rows=5, cols=3, subplot_titles=states)

    state_stat = defaultdict(dict)
    i = 0
    for k in range(1, 6):
        for j in range(1, 4):
            try:
                state_name = states[i]
            except IndexError:
                break
            state_df = state_cumulative[state_cumulative.state == states[i]]
            actual = state_df[~state_df.daily.isna()]
            state_stat[state_name]["ytd_growth"] = (
                actual.cumulative_daily_donations.iat[-1]
                - actual.cumulative_daily_donations_prev_year.iat[-1]
            ) / actual.cumulative_daily_donations_prev_year.iat[-1]
            if state_stat[state_name]["ytd_growth"] > 0:
                state_stat[state_name]["emoji"] = "🟢"
            else:
                state_stat[state_name]["emoji"] = "🔴"
            state_stat[state_name]["daily"] = actual.daily.iat[-1]
            if (
                actual.cumulative_daily_donations.iat[-1]
                > actual.cumulative_daily_donations_prev_year.iat[-1]
            ):
                colour = "green"
            else:
                colour = "red"

            fig.add_trace(
                go.Scatter(
                    x=state_df["date"],
                    y=state_df["cumulative_daily_donations_prev_year"],
                    name="2023",
                    line=dict(color="grey", dash="dot"),
                ),
                row=k,
                col=j,
            )
            fig.add_trace(
                go.Scatter(
                    x=state_df["date"],
                    y=state_df["cumulative_daily_donations"],
                    name="2024",
                    # mode='lines+markers',
                    line=dict(color=colour),
                ),
                row=k,
                col=j,
            )
            fig.add_annotation(
                x=actual["date"].iat[-1],
                y=actual["cumulative_daily_donations_prev_year"].iat[-1],
                text=f'2023: {actual["cumulative_daily_donations_prev_year"].iat[-1]}',
                showarrow=True,
                ax=20,
                ay=25,
                arrowhead=5,
                arrowcolor="grey",
                row=k,
                col=j,
            )
            fig.add_annotation(
                x=actual["date"].iat[-1],
                y=actual["cumulative_daily_donations"].iat[-1],
                text=f'2024: {actual["cumulative_daily_donations"].iat[-1]}',
                showarrow=True,
                ax=-20,
                ay=-25,
                arrowhead=5,
                arrowcolor="black",
                row=k,
                col=j,
            )

            i += 1
    fig.update_layout(
        title_text="State YTD cumulative blood donations", showlegend=False
    )
    fig.write_image("state_cumulative.png", width=1200, height=1000)
    state_stat = dict(state_stat)
    message = f"""Top 3 States: Daily Donations (YTD comparison growth)
	
	"""
    message += "\n".join(
        [
            f'{s}: {state_stat[s]["daily"]}  ({state_stat[s]["emoji"]}{state_stat[s]["ytd_growth"]*100:.1f}%)'
            for s in sorted(
                state_stat, key=lambda x: state_stat[x]["daily"], reverse=True
            )
        ]
    )
    return message


def recurrency():
    recurrency_rates_query = read_sql("sql/recurrency.sql")
    recurrency_rates_df = pd.read_gbq(
        query=recurrency_rates_query, project_id="articulate-case-410317"
    )
    recurrency_rates_df_today = (
        recurrency_rates_df[
            recurrency_rates_df.visit_date == recurrency_rates_df.visit_date.max()
        ]
        .groupby(by="donor_id")
        .max()["donation_num"]
        .value_counts()
        .sort_index()
        .reset_index()
        .rename(columns={"index": "donation_num", "count": "donor_num"})
    )

    print(recurrency_rates_df_today.head(10))
    recurrency_rates_df_today[
        "donation_num"
    ] -= 1  # to show the number of donations made before the last donation

    recurrency_rates_df_past = (
        recurrency_rates_df[
            recurrency_rates_df.visit_date < recurrency_rates_df.visit_date.max()
        ]
        .groupby(by="donor_id")
        .max()
    )
    ## donors can only donate a maximum of 2 months interval
    recurrency_rates_df_past = (
        recurrency_rates_df_past[
            recurrency_rates_df_past.visit_date
            < recurrency_rates_df.visit_date.max() - pd.Timedelta(8, "W")
        ]["donation_num"]
        .value_counts()
        .reset_index()
        .sort_index()
        .rename(columns={"index": "donation_num", "count": "donor_num"})
    )

    recurrency_rates_df_merged = recurrency_rates_df_past.merge(
        recurrency_rates_df_today, on="donation_num", how="left"
    )

    bins = [
        0,
        1,
        2,
        3,
        4,
        10,
        20,
        30,
        40,
        50,
        max(recurrency_rates_df_merged.donation_num.unique()),
    ]
    group_names = [
        "1",
        "2",
        "3",
        "4",
        "5-10",
        "11-20",
        "21-30",
        "31-40",
        "41-50",
        ">51",
    ]
    recurrency_rates_df_merged["amount_of_donations_made"] = pd.cut(
        recurrency_rates_df_merged["donation_num"], bins, labels=group_names
    )

    recurrency_rates_df_merged = recurrency_rates_df_merged.groupby(
        by="amount_of_donations_made"
    ).sum()[["donor_num_x", "donor_num_y"]]

    recurrency_rates_df_merged["perc_recurrent"] = (
        recurrency_rates_df_merged["donor_num_y"]
        / recurrency_rates_df_merged["donor_num_x"]
        * 100
    )

    recurrency_rates_df_merged = recurrency_rates_df_merged.rename(
        columns={"donor_num_y": "total_donors"}
    )
    recurrency_rates_df_merged = recurrency_rates_df_merged.reset_index()

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=[
            "Number of donations by nth time donors",
            "Percentage of recurrency by nth time donors",
        ],
        column_widths=[0.3, 0.7],
        specs=[[{"type": "pie"}, {"type": "bar"}]],
    )

    fig.add_trace(
        go.Pie(
            labels=recurrency_rates_df_merged["amount_of_donations_made"],
            values=recurrency_rates_df_merged["total_donors"],
            text=[
                f"{va: .0f}" for va in recurrency_rates_df_merged["total_donors"].values
            ],
            marker=dict(
                colors=[
                    "rgb(255,255,229)",
                    "rgb(247,252,185)",
                    "rgb(217,240,163)",
                    "rgb(173,221,142)",
                    "rgb(120,198,121)",
                    "rgb(65,171,93)",
                    "rgb(35,132,67)",
                    "rgb(0,104,55)",
                    "rgb(0,69,41)",
                    "rgb(0,0,0)",
                ]
            ),
        ),
        1,
        1,
    )

    fig.add_trace(
        go.Bar(
            x=recurrency_rates_df_merged["amount_of_donations_made"],
            y=recurrency_rates_df_merged["perc_recurrent"],
            text=[
                f"{va: .2f}%"
                for va in recurrency_rates_df_merged["perc_recurrent"].values
            ],
            textposition="auto",
            showlegend=False,
            marker=dict(
                color=[
                    "rgb(255,255,229)",
                    "rgb(247,252,185)",
                    "rgb(217,240,163)",
                    "rgb(173,221,142)",
                    "rgb(120,198,121)",
                    "rgb(65,171,93)",
                    "rgb(35,132,67)",
                    "rgb(0,104,55)",
                    "rgb(0,69,41)",
                    "rgb(0,0,0)",
                ]
            ),
        ),
        1,
        2,
    )

    fig.write_image("reccurence_stat.png", width=1200, height=1000)

    message = f"""On {recurrency_rates_df.visit_date.max()}:
	Recurring 1st time donors: {recurrency_rates_df_merged[recurrency_rates_df_merged.amount_of_donations_made=="1"]["total_donors"].iloc[0]} ({recurrency_rates_df_merged[recurrency_rates_df_merged.amount_of_donations_made=="1"]["perc_recurrent"].iloc[0]} of all 1st time donors)
	
	Most Active donor groups:
	- Highest recurrence percentage: {recurrency_rates_df_merged.sort_values(by="perc_recurrent",ascending=False).amount_of_donations_made.iloc[0]} ({recurrency_rates_df_merged.sort_values(by="perc_recurrent",ascending=False).perc_recurrent.iloc[0]}%)
	- Highest recurrence amount of donors: {recurrency_rates_df_merged.sort_values(by="total_donors",ascending=False).amount_of_donations_made.iloc[0]} ({recurrency_rates_df_merged.sort_values(by="total_donors",ascending=False).total_donors.iloc[0]}%)
	"""
    return message


def send__telegram_photo(token, chat_id, image_path, image_caption=""):
    url = f"https://api.telegram.org/bot{token}/sendPhoto?chat_id={chat_id}&caption={image_caption}"
    with open(image_path, "rb") as image_file:
        ret = requests.post(url, files={"photo": image_file})
    print(ret.json())
    print(token, chat_id, image_path, image_caption)
    return ret.json()


if __name__ == "__main__":
    malaysia_cumulative_msg = malaysia_cumulative_analytics()
    state_cumulative_analytics_msg = state_cumulative_analytics()
    recurrency_msg = recurrency()

    with open("/app/token.txt", "r") as t:
        t_token = t.read()
    with open("/app/channel.txt", "r") as t:
        t_channel = t.read()

    send__telegram_photo(
        t_token, t_channel, "malaysia_cumulative.png", malaysia_cumulative_msg
    )
    send__telegram_photo(
        t_token, t_channel, "state_cumulative.png", state_cumulative_analytics_msg
    )
    send__telegram_photo(t_token, t_channel, "reccurence_stat.png", recurrency_msg)
