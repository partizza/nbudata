from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from datetime import date, timedelta, datetime

from exchange import get_rates

app = Dash(external_stylesheets=[dbc.themes.SPACELAB])

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("NBU exchange rates"), width={"size": "auto", "offset": 4})),
    dbc.Row([
        dbc.Col(html.Label('Period'), width={"size": "auto", "offset": 1}, align='center'),
        dbc.Col(dcc.DatePickerRange(
            id='date-range',
            min_date_allowed=date(2000, 1, 1),
            max_date_allowed=date.today(),
            display_format="D.M.YYYY",
            start_date=date.today() - timedelta(days=31),
            end_date=date.today()
        ), width={"size": "auto", "offset": 0})
    ]),
    dbc.Row(dcc.Graph(id="er-graph")),
    dbc.Row(html.Hr()),
    dbc.Row([dbc.Col(id="er-table")
             ])
])


@callback(Output("er-graph", "figure"),
          Output("er-table", "children"),
          Input('date-range', 'start_date'),
          Input('date-range', 'end_date'),
          )
def update_page(start, end):
    date_format = '%Y-%m-%d'
    usd_rates = get_rates("USD", datetime.strptime(start, date_format).date(),
                          datetime.strptime(end, date_format).date())
    eur_rates = get_rates("EUR", datetime.strptime(start, date_format).date(),
                          datetime.strptime(end, date_format).date())

    fg = update_chart(usd_rates, eur_rates)
    tbl = update_table(usd_rates, eur_rates)

    return fg, tbl


def update_table(usd_rates, eur_rates):
    df_usd = pd.DataFrame(usd_rates)
    df_usd = df_usd.rename(columns={'rate_per_unit': 'USD'})
    df_usd = df_usd.loc[:, ['exchangedate', 'USD']]

    df_eur = pd.DataFrame(eur_rates)
    df_eur = df_eur.rename(columns={'rate_per_unit': 'EUR'})
    df_eur = df_eur.loc[:, ['exchangedate', 'EUR']]

    df = pd.merge(df_usd, df_eur, on='exchangedate', how='inner')
    df['exchangedate'] = pd.to_datetime(df['exchangedate'], format='%d.%m.%Y')
    df = df.sort_values(by='exchangedate', ascending=False)
    df['Date'] = df['exchangedate'].dt.strftime('%d.%m.%Y')
    df = df.loc[:, ['Date', 'USD', 'EUR']]

    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)


def update_chart(usd_rates, eur_rates) -> go.Figure:
    df = pd.concat([pd.DataFrame(usd_rates), pd.DataFrame(eur_rates)], ignore_index=True)
    df = df.rename(columns={'cc': 'Currency',
                            'exchangedate': "Date",
                            "rate_per_unit": "Exchange rate"})
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
    df = df.loc[:, ['Currency', 'Date', 'Exchange rate']]

    df = df.sort_values(by='Date')
    fg = px.line(df, x='Date', y='Exchange rate', color='Currency')

    fg.update_layout(
        title=dict(font=dict(color='black'),
                   x=0.5
                   ),
        xaxis=dict(
            title=dict(
                text='Date'
            )
        ),
        yaxis=dict(
            title=dict(
                text='Exchange rates'
            )
        ),
    )

    return fg


if __name__ == "__main__":
    app.run(debug=False)
