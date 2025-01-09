import requests
import json
import os

URL_JSON = 'https://bank.gov.ua/depo_securities?json'

JSON_DESC = {
    "cpcode": "ISIN цінного паперу",
    "nominal": "Номінал (грн.)",
    "auk_proc": "процентна ставка",
    "pgs_date": "дата погашення",
    "razm_date": "дата первинного розміщення",
    "pay_period": "період виплати відсотків (у днях)",
    "val_code": "Код валюти",
    "cptype": "Тип ЦП (DCP - ДЦП,OMP - муніціпальні)",
    "cpdescr": "Опис ЦП",
    "emit_okpo": "ЄДРПОУ емітента",
    "emit_name": "Назва емітента",
    "total_bonds": "кількість облігацій в обігу",
    "payments": "Платежі",
    "pay_date": "дата виплати відсотків",
    "pay_type": "тип виплати (1–відсоткі,2-погаш.,3-достр.погаш)",
    "pay_val": "купон виплати за 1 папір"
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


def filter_isins(data: json, isins: tuple) -> json:
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


def view(*isins) -> None:
    """
    Prints to console government bonds information

    :param isins: isin(s) to select from all data
    :return: selected government bond data
    """
    data = filter_isins(get_json(), isins)
    print(json.dumps(data, indent=6))


def to_file(*isins, dir_path: str = '.') -> None:
    """
    Writes government bonds data into files into specified directory (each isin into separate file)

    :param isins: isin(s) to select from available data
    :param dir_path: directory to write file(s)
    """
    data = filter_isins(get_json(), isins)
    for item in data:
        file_path = os.path.join(dir_path, item['cpcode'] + '.json')
        ext_item = {"desc": JSON_DESC, "data": item}
        with open(file_path, 'w') as f:
            json.dump(ext_item, f, indent=6, ensure_ascii=False)
