import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dataclasses import dataclass

from datetime import date, datetime
from tabulate import tabulate


@dataclass
class RequestBuilder:
    """
    Class to build url with its parameters
    """

    date_from: date
    date_to: date
    currency: str
    sort_by: str
    is_sort_desc: bool = True
    url: str = 'https://bank.gov.ua/NBU_Exchange/exchange_site'
    is_json_format: bool = True

    def build(self):
        """
        Build url and it's parameters that could be used to make HTTP request

        :return: url, url_params
        """

        url_params = {
            'start': self.date_from.strftime("%Y%m%d"),
            'end': self.date_to.strftime("%Y%m%d"),
            'valcode': self.currency,
            'sort': self.sort_by,
            'order': 'desc' if self.is_sort_desc else 'asc'
        }

        if self.is_json_format:
            url_params['json'] = True

        return self.url, url_params


@dataclass
class ResponseAttributes:
    exchange_date = 'exchangedate'
    currency_code = 'r030'
    currency = 'cc'
    currency_text = 'txt'
    currency_en_text = 'enname'
    rate = 'rate'
    units = 'units'
    rate_per_unit = 'rate_per_unit'
    group = 'group'
    calc_date = 'calcdate'


def get_rates(currency: str, from_date: date, to_date: date) -> json:
    """
    Request NBU exchange rates in json format for specified currency and period

    :param currency: string of requested currency exchange rates
    :param from_date: date as start of requested period
    :param to_date: date as end of requested period
    :return: json
    """

    req = RequestBuilder(date_from=from_date,
                         date_to=to_date,
                         currency=currency,
                         sort_by=ResponseAttributes.exchange_date
                         )

    url, url_params = req.build()
    res = requests.get(url, params=url_params)

    if res.status_code == 200:
        return res.json()
    else:
        print(f'Can\'t get data. Reason: {res.reason}. Status: {res.status_code}')
        return None


def chart(currency: str, from_date: date, to_date: date) -> None:
    """
    Show chart of exchange rates for requested currency and period

    :param currency: string of requested currency exchange rates
    :param from_date: date as start of requested period
    :param to_date: date as end of requested period
    :return: None
    """

    rates = get_rates(currency, from_date, to_date)

    df = pd.DataFrame(rates)
    df[ResponseAttributes.exchange_date] = pd.to_datetime(df[ResponseAttributes.exchange_date], format='%d.%m.%Y')

    fig, ax = plt.subplots()
    ax.plot(df[ResponseAttributes.exchange_date], df[ResponseAttributes.rate])
    # date axis configs
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    ax.xaxis.set_major_locator(mdates.DayLocator())

    ax.set_xlabel('Days')
    ax.set_ylabel('Exchange Rates')
    ax.set_title(f'{currency}, exchange rates')

    plt.show()


def table(currency: str, from_date: date, to_date: date) -> None:
    """
    Shows exchange rates for requested currency and period

    :param currency: string of requested currency exchange rates
    :param from_date: date as start of requested period
    :param to_date: date as end of requested period
    :return: None
    """

    rates = get_rates(currency, from_date, to_date)

    df = pd.DataFrame(rates)
    df = df[[ResponseAttributes.exchange_date, ResponseAttributes.rate]]

    print(tabulate(df, headers=['Date', f'{currency.upper()} rate'], tablefmt='pretty'))


if __name__ == '__main__':

    import argparse


    def valid_date(s: str) -> date:
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            raise argparse.ArgumentTypeError(f"not a valid date: {s!r}")


    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--currency", help="Currency code (e.g. USD, EUR)", required=True)
    parser.add_argument("-s", "--period-start", help="Period start date -- formar YYYY-MM-DD", required=True,
                        type=valid_date)
    parser.add_argument("-e", "--period-end", help="Period end date -- formar YYYY-MM-DD", required=True,
                        type=valid_date)
    args = parser.parse_args()

    table(args.currency, args.period_start, args.period_end)
    # chart(args.currency, args.period_start, args.period_end)
