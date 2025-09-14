import pandas as pd
import requests
import json
import os
from datetime import date
from tabulate import tabulate

URL_JSON = 'https://bank.gov.ua/depo_securities?json'


class ResponseAttributes:
    cpcode = 'cpcode'
    nominal = "nominal"
    auk_proc = "auk_proc"
    pgs_date = "pgs_date"
    razm_date = "razm_date"
    pay_period = "pay_period"
    val_code = "val_code"
    cptype = "cptype"
    cpdescr = "cpdescr"
    emit_okpo = "emit_okpo"
    emit_name = "emit_name"
    total_bonds = "total_bonds"
    payments = "payments"
    pay_date = "pay_date"
    pay_type = "pay_type"
    pay_val = "pay_val"

    @staticmethod
    def json_desc():
        return {
            ResponseAttributes.cpcode: "ISIN цінного паперу",
            ResponseAttributes.nominal: "Номінал (грн.)",
            ResponseAttributes.auk_proc: "процентна ставка",
            ResponseAttributes.pgs_date: "дата погашення",
            ResponseAttributes.razm_date: "дата первинного розміщення",
            ResponseAttributes.pay_period: "період виплати відсотків (у днях)",
            ResponseAttributes.val_code: "Код валюти",
            ResponseAttributes.cptype: "Тип ЦП (DCP - ДЦП,OMP - муніціпальні)",
            ResponseAttributes.cpdescr: "Опис ЦП",
            ResponseAttributes.emit_okpo: "ЄДРПОУ емітента",
            ResponseAttributes.emit_name: "Назва емітента",
            ResponseAttributes.total_bonds: "кількість облігацій в обігу",
            ResponseAttributes.payments: "Платежі",
            ResponseAttributes.pay_date: "дата виплати відсотків",
            ResponseAttributes.pay_type: "тип виплати (1–відсоткі,2-погаш.,3-достр.погаш)",
            ResponseAttributes.pay_val: "купон виплати за 1 папір"
        }


def get_json() -> json:
    """
    Makes HTTP GET request to NBU API to retrieve government bonds info

    :return: json data
    """
    res = requests.get(URL_JSON)

    if res.status_code == 200:
        return res.json()
    else:
        print(f'Can\'t get data. Reason: {res.reason}. Status: {res.status_code}')
        return None


def filter_isins(data: json, isins: list) -> json:
    """
    Filter source json government bonds data by isin(s)

    :param data: government bonds data in json format
    :param isins: isin value(s) to filter
    :return: json data filtered by isin(s)
    """
    if isins:
        return [item for item in data if item['cpcode'] in isins]
    else:
        return data


def show(isins: list, format: str) -> None:
    """
    Prints to console government bonds information

    :param isins: isin(s) to select from all data
    :param format: view format
    """
    data = filter_isins(get_json(), isins)
    f = format.lower()

    if f == 'json':
        print(json.dumps(data, indent=6, ensure_ascii=False))

    elif f == 'table':
        df = pd.DataFrame(data)
        df = df.drop(columns=ResponseAttributes.payments)
        print(tabulate(df, headers='keys', showindex=False, tablefmt='rst', disable_numparse=True))

    else:
        raise AttributeError(f"Unknown format: {format}")


def show_payments(isins: list, include_paid: bool) -> None:
    """
    Prints to console aggregated payment per bond on each payment date.

    :param isins: selected ISINs
    :param include_paid: if True includes passed payment dates, otherwise only expected payments
    """

    data = filter_isins(get_json(), isins)
    df = pd.DataFrame(data)
    df = df.explode(ResponseAttributes.payments)
    df_exploded = df[ResponseAttributes.payments].apply(pd.Series)
    df = pd.concat([df.drop(ResponseAttributes.payments, axis=1), df_exploded], axis=1)
    df = df.groupby([ResponseAttributes.pay_date, ResponseAttributes.val_code], as_index=False).agg(
        pay_per_bond=(ResponseAttributes.pay_val, 'sum'))
    df[ResponseAttributes.pay_date] = pd.to_datetime(df[ResponseAttributes.pay_date]).dt.date
    if not include_paid:
        df = df.loc[df[ResponseAttributes.pay_date] >= date.today()]

    df.sort_values(by=[ResponseAttributes.pay_date, ResponseAttributes.val_code])

    print(tabulate(df, headers='keys', showindex=False))


def to_file(isins: list, dir_path: str = '.') -> None:
    """
    Writes government bonds data into files into specified directory (each isin into separate file)

    :param isins: isin(s) to select from available data
    :param dir_path: directory to write file(s)
    """

    data = filter_isins(get_json(), isins)
    for item in data:
        file_path = os.path.join(dir_path, item['cpcode'] + '.json')
        ext_item = {"desc": ResponseAttributes.json_desc(), "data": item}
        with open(file_path, 'w') as f:
            json.dump(ext_item, f, indent=6, ensure_ascii=False)


def save(isins: list, file: str) -> None:
    """
    Writes data into file in json format

    :param isins: selected ISINs to write
    :param file: name of file to write into
    """

    data = filter_isins(get_json(), isins)
    with open(file, 'w') as f:
        json.dump(data, f, indent=6, ensure_ascii=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f"Script to retrieve government bounds data form NBU API ({URL_JSON})",
        epilog="""Example: 
            1. Save all data into file data.json:
                    %(prog)s save -f data.json
            2. Show bonds filtered by isin:
                    %(prog)s -s UA4000227193,UA4000227201 show
            """)

    parser.add_argument('-s', '--isin',
                        help="""
                                Filter by ISIN code(s), split the values by comma if more than one, 
                                e.g. -s UA12,UA05,UA78
                                """)

    subparsers = parser.add_subparsers(required=True, help="Available commands.")

    show_parser = subparsers.add_parser('show', help="Shows data on console")
    show_parser.add_argument('--show-format', default='table', choices=['table', 'json'],
                             help="Specifies how data shown on console.")

    save_parser = subparsers.add_parser('save', help='Saves data into file')
    save_parser.add_argument('-f', '--file-export', help='File to save data. Skip save If file name is missing.')

    payments_parser = subparsers.add_parser('payments', help='Shows payments by dates')
    payments_parser.add_argument('-a', action='store_true',
                                 help="Shows all payments (paid and unpaid. In other case it shows only unpaid payments.")

    args = parser.parse_args()
    isins = args.isin.split(',') if args.isin else None

    if 'show_format' in args:
        show(isins, args.show_format)
    elif 'file_export' in args:
        save(isins, args.file_export)
    elif 'a' in args:
        show_payments(isins, args.a)
