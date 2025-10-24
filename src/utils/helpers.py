import logging
from typing import Dict, List, Optional

from src.models.vacancy import Vacancy


def convert_to_vacancy_objects(data: List[Dict]) -> List[Vacancy]:
    """
    Конвертация сырых данных из API в объекты Vacancy
    :param data: Список словарей с данными вакансий
    :return: Список объектов Vacancy
    """
    vacancies = []

    if not data or not isinstance(data, list):
        return vacancies

    for item in data:
        if not isinstance(item, dict):
            continue

        try:
            # Извлекаем данные с проверкой на наличие
            salary = item.get("salary") or {}
            snippet = item.get("snippet") or {}
            employer = item.get("employer") or {}
            address = item.get("address") or {}

            # Обработка зарплаты
            salary_from = salary.get("from")
            salary_to = salary.get("to")
            salary_currency = salary.get("currency", "RUR")

            # Конвертируем зарплату в рубли если нужно
            if salary_currency != "RUR" and (salary_from or salary_to):
                # Здесь можно добавить логику конвертации валют
                # Для упрощения оставляем как есть
                pass

            # Очистка строк от проблемных символов
            title = clean_string(item.get("name", ""))
            url = item.get("alternate_url", "")

            # Объединяем requirement и responsibility для полного описания
            requirement = clean_string(snippet.get("requirement", ""))
            responsibility = clean_string(snippet.get("responsibility", ""))
            description = f"{responsibility}\n{requirement}".strip()

            employer_name = clean_string(employer.get("name", ""))

            # Извлекаем город
            city = address.get("city", "") if address else ""
            if city:
                description = f"Город: {city}\n{description}"

            # Создаем объект Vacancy только если есть минимально необходимые данные
            if title and employer_name:
                vacancy = Vacancy(
                    title=title,
                    url=url,
                    salary_from=salary_from,
                    salary_to=salary_to,
                    description=description or "Описание не указано",
                    employer=employer_name,
                )
                vacancies.append(vacancy)

        except Exception as e:
            logging.error(f"Ошибка при создании вакансии из данных {item.get('name', 'Unknown')}: {e}")
            continue

    return vacancies


def clean_string(text: str) -> str:
    """
    Очистка строки от проблемных символов и лишних пробелов
    :param text: Исходный текст
    :return: Очищенный текст
    """
    if not text:
        return ""

    # Удаляем HTML теги и лишние пробелы
    import re
    text = re.sub(r'<[^>]+>', '', str(text))
    text = ' '.join(text.split())

    return text.encode('utf-8', 'ignore').decode('utf-8').strip()


def filter_vacancies(vacancies: List[Vacancy], filter_words: List[str]) -> List[Vacancy]:
    """
    Фильтрация вакансий по ключевым словам
    :param vacancies: Список вакансий
    :param filter_words: Список ключевых слов
    :return: Отфильтрованный список вакансий
    """
    if not filter_words or not vacancies:
        return vacancies

    filtered = []
    for vacancy in vacancies:
        if not vacancy:
            continue

        description = (vacancy.description or "").lower()
        title = (vacancy.title or "").lower()
        employer = (vacancy.employer or "").lower()

        # Ищем ключевые слова в разных полях
        search_text = f"{title} {description} {employer}"

        if any(word.lower() in search_text for word in filter_words if word.strip()):
            filtered.append(vacancy)

    return filtered


def sort_vacancies_by_salary(vacancies: List[Vacancy], descending: bool = True) -> List[Vacancy]:
    """
    Сортировка вакансий по зарплате
    :param vacancies: Список вакансий
    :param descending: По убыванию (True) или возрастанию (False)
    :return: Отсортированный список
    """

    def get_max_salary(vacancy):
        """Вспомогательная функция для получения максимальной зарплаты"""
        return max(
            vacancy.salary_from or 0,
            vacancy.salary_to or 0,
            (vacancy.salary_from or 0 + vacancy.salary_to or 0) // 2
        )

    return sorted(vacancies, key=get_max_salary, reverse=descending)


def remove_duplicate_vacancies(vacancies: List[Vacancy]) -> List[Vacancy]:
    """
    Удаление дубликатов вакансий по URL
    :param vacancies: Список вакансий
    :return: Список без дубликатов
    """
    seen_urls = set()
    unique_vacancies = []

    for vacancy in vacancies:
        if vacancy.url and vacancy.url not in seen_urls:
            seen_urls.add(vacancy.url)
            unique_vacancies.append(vacancy)

    return unique_vacancies