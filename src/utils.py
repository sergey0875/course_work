import json
from datetime import datetime
from typing import Any

import pandas as pd
import requests


def import_excel_data(file_path: str) -> list[dict[str, Any]]:
    """Считывает Excel и сразу возвращает список словарей."""
    df = pd.read_excel(file_path)
    return df.to_dict(orient="records")


def filter_by_date(transactions: list[dict[str, Any]], date_str: str) -> list[dict[str, Any]]:
    """Фильтрует список словарей с начала месяца по указанную дату."""

    end_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start_date = end_date.replace(day=1, hour=0, minute=0, second=0)

    filtered_list = []
    for item in transactions:
        # Превращаем строку даты из Excel в объект datetime
        op_date = datetime.strptime(str(item["Дата операции"]), "%d.%m.%Y %H:%M:%S")

        if start_date <= op_date <= end_date:
            filtered_list.append(item)

    return filtered_list


def get_cards_stats(transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Считает расходы и кешбэк по каждой карте через обычный словарь."""
    cards_totals = {}

    for item in transactions:
        card = item.get("Номер карты")
        amount = item.get("Сумма операции", 0)

        if isinstance(card, str) and amount < 0:
            # Если карты еще нет в словаре, добавляем её с нулем, затем прибавляем трату
            cards_totals[card] = cards_totals.get(card, 0.0) + abs(float(amount))

    result = []
    for card, total in cards_totals.items():
        total_rounded = round(total, 2)
        result.append(
            {"last_digits": card[-4:], "total_spent": total_rounded, "cashback": round(total_rounded / 100, 2)}
        )

    return result


def get_top_transactions(transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Возвращает топ-5 транзакций по сумме платежа."""
    # Сортируем список словарей по модулю суммы платежа от большего к меньшему
    sorted_tx = sorted(transactions, key=lambda x: abs(float(x.get("Сумма платежа", 0))), reverse=True)

    top_5 = []
    for item in sorted_tx[:5]:
        top_5.append(
            {
                "date": str(item["Дата платежа"]),
                "amount": round(abs(float(item["Сумма платежа"])), 2),
                "category": str(item["Категория"]),
                "description": str(item["Описание"]),
            }
        )
    return top_5


def get_greeting(date_str: str) -> str:
    """Функция приветствия по времени."""
    data_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    hour = data_obj.hour

    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    return "Доброй ночи"


def get_user_settings(filepath: str) -> dict:
    """Читает файл настроек user_settings.json."""

    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def get_currency_rates(currencies: list[str]) -> list[dict]:
    """Получает курсы валют к рублю через API ЦБ РФ (работает в РФ без ключей)."""
    url = "https://www." + "cbr-xml-daily.ru" + "/daily_json.js"
    result = []
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        for currency in currencies:
            if currency in data.get("Valute", {}):
                rate = round(data["Valute"][currency]["Value"], 2)
                result.append({"currency": currency, "rate": rate})
    except Exception as e:
        print(f"Ошибка при получении курсов валют: {e}")

    return result


def get_stock_prices(stocks: list[str]) -> list[dict]:
    """Получает цены акций S&P 500 через TradingView Scanner API (работает в РФ без ключей)."""
    url = "https://scanner." + "tradingview.com" + "/america/scan"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json",
    }

    tickers = []
    for stock in stocks:
        tickers.append(f"NASDAQ:{stock}")
        tickers.append(f"NYSE:{stock}")

    payload = {"symbols": {"tickers": tickers}, "columns": ["name", "close"]}

    result = []
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        prices_map = {}
        for item in data.get("data", []):
            values = item.get("d", [])
            if len(values) >= 2:
                ticker_name, close_price = values
                if close_price is not None:
                    prices_map[ticker_name] = round(float(close_price), 2)

        for stock in stocks:
            if stock in prices_map:
                result.append({"stock": stock, "price": prices_map[stock]})
    except Exception as e:
        print(f"Ошибка при получении цен акций: {e}")

    return result
