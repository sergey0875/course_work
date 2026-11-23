import json
from unittest.mock import Mock
from unittest.mock import mock_open
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import filter_by_date
from src.utils import get_cards_stats
from src.utils import get_currency_rates
from src.utils import get_greeting
from src.utils import get_stock_prices
from src.utils import get_top_transactions
from src.utils import get_user_settings
from src.utils import import_excel_data


@pytest.fixture
def sample_transactions() -> list[dict]:
    """Фикстура с набором тестовых транзакций."""
    return [
        {
            "Дата операции": "01.12.2021 10:00:00",
            "Дата платежа": "01.12.2021",
            "Номер карты": "*7197",
            "Сумма операции": -1000.0,
            "Сумма платежа": -1000.0,
            "Категория": "Супермаркеты",
            "Описание": "Пятерочка",
        },
        {
            "Дата операции": "15.12.2021 14:30:00",
            "Дата платежа": "15.12.2021",
            "Номер карты": "*7197",
            "Сумма операции": -2500.5,
            "Сумма платежа": -2500.5,
            "Категория": "Рестораны",
            "Описание": "Кафе",
        },
        {
            "Дата операции": "20.12.2021 18:00:00",
            "Дата платежа": "20.12.2021",
            "Номер карты": "*4556",
            "Сумма операции": -500.0,
            "Сумма платежа": -500.0,
            "Категория": "Транспорт",
            "Описание": "Такси",
        },
        {
            "Дата операции": "25.12.2021 12:00:00",
            "Дата платежа": "25.12.2021",
            "Номер карты": "*7197",
            "Сумма операции": -10000.0,
            "Сумма платежа": -10000.0,
            "Категория": "Авиабилеты",
            "Описание": "Аэрофлот",
        },
        {
            "Дата операции": "10.12.2021 09:00:00",
            "Дата платежа": "10.12.2021",
            "Номер карты": "*7197",
            "Сумма операции": 50000.0,
            "Сумма платежа": 50000.0,
            "Категория": "Пополнения",
            "Описание": "Зарплата",
        },
        {
            "Дата операции": "05.12.2021 11:00:00",
            "Дата платежа": "05.12.2021",
            "Номер карты": None,
            "Сумма операции": -300.0,
            "Сумма платежа": -300.0,
            "Категория": "Переводы",
            "Описание": "Перевод",
        },
    ]


@patch("src.utils.pd.read_excel")
def test_import_excel_data(mock_read_excel):
    mock_read_excel.return_value = pd.DataFrame([{"Категория": "Еда", "Сумма операции": -100}])
    result = import_excel_data("test.xlsx")

    mock_read_excel.assert_called_once_with("test.xlsx")
    assert result == [{"Категория": "Еда", "Сумма операции": -100}]


def test_filter_by_date(sample_transactions):

    result = filter_by_date(sample_transactions, "2021-12-20 23:59:59")
    assert len(result) == 5
    dates = [tx["Дата операции"] for tx in result]
    assert "25.12.2021 12:00:00" not in dates


def test_get_cards_stats(sample_transactions):
    result = get_cards_stats(sample_transactions)

    assert len(result) == 2
    assert {"last_digits": "7197", "total_spent": 13500.5, "cashback": 135.0} in result
    assert {"last_digits": "4556", "total_spent": 500.0, "cashback": 5.0} in result


def test_get_top_transactions(sample_transactions):
    result = get_top_transactions(sample_transactions)
    assert len(result) == 5
    assert result[0]["amount"] == 50000.0
    assert result[0]["category"] == "Пополнения"
    assert result[1]["amount"] == 10000.0
    assert result[1]["category"] == "Авиабилеты"


@pytest.mark.parametrize(
    "date_str, expected",
    [
        ("2021-12-20 06:00:00", "Доброе утро"),
        ("2021-12-20 14:30:00", "Добрый день"),
        ("2021-12-20 20:15:00", "Добрый вечер"),
        ("2021-12-20 02:00:00", "Доброй ночи"),
    ],
)
def test_get_greeting(date_str, expected):
    assert get_greeting(date_str) == expected


def test_get_user_settings():
    mock_data = json.dumps({"user_currencies": ["USD"], "user_stocks": ["AAPL"]})
    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = get_user_settings("user_settings.json")
        assert result == {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}


@patch("src.utils.requests.get")
def test_get_currency_rates_success(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {
        "Valute": {
            "USD": {"Value": 85.456},
            "EUR": {"Value": 92.123},
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = get_currency_rates(["USD", "EUR", "CNY"])
    assert result == [
        {"currency": "USD", "rate": 85.46},
        {"currency": "EUR", "rate": 92.12},
    ]


@patch("src.utils.requests.get", side_effect=Exception("Network error"))
def test_get_currency_rates_error(mock_get):
    result = get_currency_rates(["USD"])
    assert result == []


@patch("src.utils.requests.post")
def test_get_stock_prices_success(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": [
            {"d": ["AAPL", 225.556]},
            {"d": ["TSLA", 240.1]},
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = get_stock_prices(["AAPL", "TSLA", "MSFT"])
    assert result == [
        {"stock": "AAPL", "price": 225.56},
        {"stock": "TSLA", "price": 240.1},
    ]


@patch("src.utils.requests.post", side_effect=Exception("API error"))
def test_get_stock_prices_error(mock_post):
    result = get_stock_prices(["AAPL"])
    assert result == []
