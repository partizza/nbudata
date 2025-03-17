import requests
import json
import os

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


def show(isins: list) -> None:
    """
    Prints to console government bonds information

    :param isins: isin(s) to select from all data
    :return: selected government bond data
    """
    data = filter_isins(get_json(), isins)
    print(json.dumps(data, indent=6, ensure_ascii=False))


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
                    %(prog)s -a save -f data.json
            2. Show bonds filtered by isin:
                    %(prog)s -s UA4000227193,UA4000227201
            """)

    parser.add_argument('-a', '--command',
                        help="""Defines how to explore data. 
                        Option 'show' prints bond descriptions onto console. 
                        Option 'save' saves bond descriptions into file.
                        By default is 'show'.
                        """,
                        nargs='?', choices=['show', 'save'], default='show')
    parser.add_argument('-s', '--isin',
                        help="""
                                Filter by ISIN code(s), split the values by comma if more than one, 
                                e.g. -s UA12,UA05,UA78
                                """)
    parser.add_argument('-f', '--file-export', help='File to save data. Skip save If file name is missing.')

    args = parser.parse_args()
    isins = args.isin.split(',') if args.isin else None

    if args.command == 'show':
        show(isins)
    elif args.command == 'save':
        print("should save")
        save(isins, args.file_export)
    else:
        raise ValueError(f'Unknown command: {args.command}')
