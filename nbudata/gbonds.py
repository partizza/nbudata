import requests
import json

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
    res = requests.get(URL_JSON)

    if res.status_code == 200:
        return res.json()
    else:
        print(f'Can\'t get data. Reason: {res.reason}. Status: {res.status_code}')
        return None


def view(*isins) -> None:
    data = get_json()

    if isins:
        filtered_isins = [item for item in data if item['cpcode'] in isins]
        print(json.dumps(filtered_isins, indent=6))
    else:
        print(json.dumps(data, indent=6))
