from typing import Dict, List

from src.models.vacancy import Vacancy


def convert_to_vacancy_objects(data: List[Dict]) -> List[Vacancy]:
    """
    Конвертация данных из API в список объектов Vacancy
    :param data: Список словарей с данными о вакансиях
    :return: Список объектов Vacancy
    """
    vacancies = []
    for item in data:
        if not isinstance(item, dict):
            continue

        salary = item.get("salary") or {}
        snippet = item.get("snippet") or {}
        employer = item.get("employer") or {}

        try:
            vacancy = Vacancy(
                title=item.get("name", ""),
                url=item.get("alternate_url", ""),
                salary_from=salary.get("from") if salary else None,
                salary_to=salary.get("to") if salary else None,
                description=snippet.get("requirement", ""),
                employer=employer.get("name", ""),
            )
            vacancies.append(vacancy)
        except ValueError as e:
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
