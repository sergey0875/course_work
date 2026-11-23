import json
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def analyze_cashback_categories(data: list[dict[str, Any]], year: int, month: int) -> str:
    """Анализирует, сколько кешбэка (5%) можно заработать по каждой категории за указанный месяц."""

    logger.info(f"Анализ категорий за {month:02d}.{year}")

    # Фильтруем только расходы (сумма < 0) за нужный год и месяц через filter + lambda
    filtered_tx = list(
        filter(
            lambda tx: (
                tx.get("Статус") != "FAILED"
                and isinstance(tx.get("Сумма операции"), (int, float))
                and tx["Сумма операции"] < 0
                and isinstance(tx.get("Категория"), str)
                and datetime.strptime(str(tx["Дата операции"])[:10], "%d.%m.%Y").year == year
                and datetime.strptime(str(tx["Дата операции"])[:10], "%d.%m.%Y").month == month
            ),
            data,
        )
    )

    # Считаем 5% кешбэка по каждой категории
    cashback_by_category: dict[str, int] = {}
    for tx in filtered_tx:
        category = tx["Категория"]
        cashback = int(abs(tx["Сумма операции"]) * 0.05)
        cashback_by_category[category] = cashback_by_category.get(category, 0) + cashback

    # Сортируем от самой выгодной категории к меньшей через sorted + lambda
    sorted_cashback = dict(sorted(cashback_by_category.items(), key=lambda item: item, reverse=True))

    return json.dumps(sorted_cashback, ensure_ascii=False, indent=4)
