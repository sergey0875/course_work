import json

from src.utils import filter_by_date
from src.utils import get_cards_stats
from src.utils import get_currency_rates
from src.utils import get_greeting
from src.utils import get_stock_prices
from src.utils import get_top_transactions
from src.utils import get_user_settings
from src.utils import import_excel_data


def main_page(date_str: str) -> str:
    """Главная функция: объединяет все данные в итоговый JSON."""

    # Загружаем настройки и транзакции
    settings = get_user_settings("C:/Users/sepaa/PycharmProjects/Сoursework/user_settings.json")
    all_transactions = import_excel_data("C:/Users/sepaa/PycharmProjects/Сoursework/data/operations.xlsx")

    # Фильтруем транзакции за текущий месяц
    filtered_tx = filter_by_date(all_transactions, date_str)

    #  Собираем словарь со всеми ключами по заданию
    response_data = {
        "greeting": get_greeting(date_str),
        "cards": get_cards_stats(filtered_tx),
        "top_transactions": get_top_transactions(filtered_tx),
        "currency_rates": get_currency_rates(settings.get("user_currencies", [])),
        "stock_prices": get_stock_prices(settings.get("user_stocks", [])),
    }

    # 4. Превращаем словарь в JSON-строку
    return json.dumps(response_data, ensure_ascii=False, indent=4)
