import pandas as pd

from src.reports import report_to_file
from src.reports import spending_by_category


def test_spending_by_category_and_decorator(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    df = pd.DataFrame(
        [
            {
                "Дата операции": "15.12.2021 12:00:00",
                "Статус": "OK",
                "Сумма операции": -1500.0,
                "Категория": "Супермаркеты",
            },
            {
                "Дата операции": "01.08.2021 10:00:00",
                "Статус": "OK",
                "Сумма операции": -3000.0,
                "Категория": "Супермаркеты",
            },
            {
                "Дата операции": "18.12.2021 18:00:00",
                "Статус": "OK",
                "Сумма операции": -1200.0,
                "Категория": "Транспорт",
            },
        ]
    )

    # Проверяем отчет за 3 месяца от 2021-12-20 и декоратор без параметров
    res = spending_by_category(df, category="Супермаркеты", date="2021-12-20")
    assert len(res) == 1
    assert list(res["Сумма операции"]) == [-1500.0]
    assert len(list(tmp_path.glob("report_spending_by_category_*.json"))) == 1

    # Проверяем декоратор с явным именем файла
    custom_file = tmp_path / "out.json"

    @report_to_file(str(custom_file))
    def sample():
        return {"ok": True}

    sample()
    assert custom_file.exists()
