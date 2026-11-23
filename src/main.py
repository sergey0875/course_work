import os

import pandas as pd
from dotenv import load_dotenv

from src.reports import spending_by_category
from src.services import analyze_cashback_categories
from src.utils import import_excel_data
from src.views import main_page

load_dotenv()

EXCEL_PATH = os.getenv("EXCEL_PATH")


def main() -> None:
    """Единая точка входа: демонстрирует работу веб-страниц, сервисов и отчетов."""
    try:
        target_date = input("Введите дату и время в формате 'Y-m-d H:M:S': ")

        print("ГЛАВНАЯ СТРАНИЦА")
        page_json = main_page(target_date)
        print(page_json)

        transactions_list = import_excel_data(EXCEL_PATH)
        transactions_df = pd.read_excel(EXCEL_PATH)

        print("ВЫГОДНЫЕ КАТЕГОРИИ КЕШБЭКА")
        cashback_json = analyze_cashback_categories(transactions_list, year=2021, month=12)
        print(cashback_json)

        print("ОТЧЕТ: ТРАТЫ ПО КАТЕГОРИИ")
        category_report = spending_by_category(
            transactions=transactions_df,
            category="Супермаркеты",
            date="2021-12-20",
        )

        print(f"Найдено операций: {len(category_report)}")
        print(category_report[["Дата операции", "Категория", "Сумма операции"]].head())
    except ValueError as f:
        print(f"Не правильный формат {f}")


if __name__ == "__main__":
    main()
