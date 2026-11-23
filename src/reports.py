import functools
import json
import logging
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Callable
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def report_to_file(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для функций-отчетов. Записывает результат работы функции в JSON-файл.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            # Определяем имя файла (если не передано — генерируем по умолчанию)
            target_file = (
                filename
                if isinstance(filename, str)
                else f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            # Если функция вернула DataFrame, преобразуем его в список словарей для JSON
            data_to_save = result.to_dict(orient="records") if isinstance(result, pd.DataFrame) else result

            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4, default=str)

            logger.info(f"Отчет успешно сохранен в файл: {target_file}")
            return result

        return wrapper

    # Поддержка вызова декоратора без скобок (@report_to_file)
    if callable(filename):
        func = filename
        filename = None
        return decorator(func)

    return decorator


@report_to_file
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние 3 месяца от переданной (или текущей) даты.
    """
    logger.info(f"Формирование отчета по категории '{category}' на дату {date or 'сегодня'}")

    # Определяем конечную и начальную даты (3 месяца ≈ 90 дней)
    end_date = datetime.strptime(date[:10], "%Y-%m-%d") if date else datetime.now()
    start_date = end_date - timedelta(days=90)

    df = transactions.copy()

    # Приводим колонку с датой к формату datetime (поддержка формата из Excel 'DD.MM.YYYY HH:MM:SS')
    df["dt_temp"] = pd.to_datetime(df["Дата операции"], dayfirst=True, errors="coerce")

    # Фильтруем: нужная категория, расход (сумма < 0), успешный статус и попадание в 3 месяца
    filtered_df = df[
        (df["Категория"] == category)
        & (df["Сумма операции"] < 0)
        & (df["Статус"] != "FAILED")
        & (df["dt_temp"] >= start_date)
        & (df["dt_temp"] <= end_date)
    ].drop(columns=["dt_temp"])

    return filtered_df
