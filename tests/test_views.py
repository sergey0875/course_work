import json
from unittest.mock import patch

from src.views import main_page


@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
@patch("src.views.get_top_transactions")
@patch("src.views.get_cards_stats")
@patch("src.views.get_greeting")
@patch("src.views.filter_by_date")
@patch("src.views.import_excel_data")
@patch("src.views.get_user_settings")
def test_main_page_success(
    mock_get_settings,
    mock_import_excel,
    mock_filter_date,
    mock_get_greeting,
    mock_get_cards,
    mock_get_top_tx,
    mock_get_currencies,
    mock_get_stocks,
):
    """Тестирует сборку итогового JSON функцией main_page с подменой всех зависимостей."""
    # 1. Задаем возвращаемые значения для каждого мока
    mock_get_settings.return_value = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "TSLA"],
    }
    mock_import_excel.return_value = [{"Дата операции": "20.12.2021 15:30:00", "Сумма операции": -1000}]
    mock_filter_date.return_value = [{"Дата операции": "20.12.2021 15:30:00", "Сумма операции": -1000}]
    mock_get_greeting.return_value = "Добрый день"
    mock_get_cards.return_value = [{"last_digits": "7197", "total_spent": 1000.0, "cashback": 10.0}]
    mock_get_top_tx.return_value = [
        {"date": "20.12.2021", "amount": 1000.0, "category": "Супермаркеты", "description": "Магазин"}
    ]
    mock_get_currencies.return_value = [{"currency": "USD", "rate": 85.5}]
    mock_get_stocks.return_value = [{"stock": "AAPL", "price": 225.0}]

    # Вызываем тестируемую функцию
    result_json_str = main_page("2021-12-20 15:30:00")

    # Проверяем, что вернулась валидная JSON-строка и парсим её обратно в словарь
    assert isinstance(result_json_str, str)
    parsed_data = json.loads(result_json_str)

    # Проверяем структуру и значения всех ключей ответа
    assert parsed_data == {
        "greeting": "Добрый день",
        "cards": [{"last_digits": "7197", "total_spent": 1000.0, "cashback": 10.0}],
        "top_transactions": [
            {"date": "20.12.2021", "amount": 1000.0, "category": "Супермаркеты", "description": "Магазин"}
        ],
        "currency_rates": [{"currency": "USD", "rate": 85.5}],
        "stock_prices": [{"stock": "AAPL", "price": 225.0}],
    }

    # Проверяем, что в функции валют и акций передались списки из настроек
    mock_get_currencies.assert_called_once_with(["USD", "EUR"])
    mock_get_stocks.assert_called_once_with(["AAPL", "TSLA"])
    mock_get_greeting.assert_called_once_with("2021-12-20 15:30:00")
