import json

import pytest

from src.services import analyze_cashback_categories


@pytest.fixture
def sample_transactions() -> list[dict]:
    """Фикстура с набором транзакций за разные месяцы и с разными статусами."""
    return [
        # Подходящие расходы за декабрь 2021
        {
            "Дата операции": "10.12.2021 12:00:00",
            "Статус": "OK",
            "Сумма операции": -20000.0,
            "Категория": "Супермаркеты",
        },
        {
            "Дата операции": "15.12.2021 15:30:00",
            "Статус": "OK",
            "Сумма операции": -10000.0,
            "Категория": "Супермаркеты",
        },
        {
            "Дата операции": "20.12.2021 18:00:00",
            "Статус": "OK",
            "Сумма операции": -40000.0,
            "Категория": "Авиабилеты",
        },
        {"Дата операции": "22.12.2021 19:15:00", "Статус": "OK", "Сумма операции": -5000.0, "Категория": "Рестораны"},
        # Неподходящие транзакции
        {
            "Дата операции": "25.12.2021 10:00:00",
            "Статус": "FAILED",
            "Сумма операции": -50000.0,
            "Категория": "Одежда",
        },
        {
            "Дата операции": "26.12.2021 11:00:00",
            "Статус": "OK",
            "Сумма операции": 100000.0,
            "Категория": "Пополнения",
        },
        {
            "Дата операции": "05.11.2021 14:00:00",
            "Статус": "OK",
            "Сумма операции": -30000.0,
            "Категория": "Электроника",
        },
        {"Дата операции": "28.12.2021 16:00:00", "Статус": "OK", "Сумма операции": -2000.0, "Категория": None},
    ]


def test_analyze_cashback_categories_success(sample_transactions):
    """Тестирует корректность расчета 5% кешбэка, фильтрацию и сортировку."""
    result_json = analyze_cashback_categories(sample_transactions, year=2021, month=12)
    result = json.loads(result_json)

    assert result == {
        "Авиабилеты": 2000,
        "Супермаркеты": 1500,
        "Рестораны": 250,
    }


@pytest.mark.parametrize(
    "year, month, expected",
    [
        (2021, 11, {"Электроника": 1500}),  # 30000 * 0.05 = 1500
        (2021, 10, {}),  # В октябре транзакций нет
        (2022, 12, {}),  # В 2022 году транзакций нет
    ],
)
def test_analyze_cashback_categories_different_periods(sample_transactions, year, month, expected):
    """Тестирует анализ за другие периоды и при отсутствии транзакций."""
    result_json = analyze_cashback_categories(sample_transactions, year=year, month=month)
    assert json.loads(result_json) == expected


def test_analyze_cashback_categories_empty_data():
    """Тестирует поведение функции при передаче пустого списка транзакций."""
    result_json = analyze_cashback_categories([], year=2021, month=12)
    assert json.loads(result_json) == {}
