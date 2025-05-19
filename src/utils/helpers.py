import logging
from typing import Dict, List

from src.models.vacancy import Vacancy


def convert_to_vacancy_objects(data: List[Dict]) -> List[Vacancy]:
    vacancies = []
    for item in data:
        if not isinstance(item, dict):
            continue

        salary = item.get("salary") or {}
        snippet = item.get("snippet") or {}
        employer = item.get("employer") or {}

        try:
            # Очистка строк от проблемных символов
            title = item.get("name", "").encode('utf-8', 'ignore').decode('utf-8')
            url = item.get("alternate_url", "")
            description = snippet.get("requirement", "").encode('utf-8', 'ignore').decode('utf-8')
            employer_name = employer.get("name", "").encode('utf-8', 'ignore').decode('utf-8')

            vacancy = Vacancy(
                title=title,
                url=url,
                salary_from=salary.get("from") if salary else None,
                salary_to=salary.get("to") if salary else None,
                description=description,
                employer=employer_name,
            )
            vacancies.append(vacancy)
        except Exception as e:
            logging.error(f"Ошибка при создании вакансии: {e}")
            continue

    return vacancies


def filter_vacancies(vacancies: List[Vacancy], filter_words: List[str]) -> List[Vacancy]:
    """
    Фильтрация вакансий по ключевым словам
    :param vacancies: Список вакансий
    :param filter_words: Список ключевых слов
    :return: Отфильтрованный список вакансий
    """
    if not filter_words:
        return vacancies

    filtered = []
    for vacancy in vacancies:
        description = (vacancy.description or "").lower()
        title = vacancy.title.lower()
        if any(word.lower() in description or word.lower() in title for word in filter_words):
            filtered.append(vacancy)
    return filtered
