from typing import Dict, List, Optional
import requests
from requests import Response
from src.api.abstract_api import AbstractAPI


class HeadHunterAPI(AbstractAPI):
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.__base_url = "https://api.hh.ru/vacancies"
        self._session = requests.Session()
        # Устанавливаем заголовки для избежания блокировки
        self._session.headers.update({
            'User-Agent': 'MyVacancyApp/1.0 (your-email@example.com)',
            'Accept': 'application/json'
        })

    def _connect_to_api(self) -> Response:
        """Приватный метод для проверки соединения с API"""
        try:
            response = self._session.get(self.__base_url, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Ошибка подключения к API HH: {e}")

    def get_vacancies(self, keyword: str, per_page: int = 100) -> List[Dict]:
        """
        Получение вакансий по ключевому слову
        :param keyword: Ключевое слово для поиска
        :param per_page: Количество результатов на страницу
        :return: Список вакансий
        """
        params = {
            "text": keyword,
            "per_page": per_page,
            "search_field": "name",
            "area": 113,  # Россия
            "only_with_salary": True  # Только вакансии с указанной зарплатой
        }

        try:
            response = self._session.get(self.__base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Валидация ответа
            if not isinstance(data, dict) or 'items' not in data:
                return []

            return data.get("items", [])

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении вакансий: {e}")
            return []
        except ValueError as e:
            print(f"Ошибка парсинга JSON: {e}")
            return []

    def get_vacancies_by_employer(self, employer_id: str, per_page: int = 50) -> List[Dict]:
        """
        Получение вакансий по конкретному работодателю
        :param employer_id: ID работодателя на HH
        :param per_page: Количество результатов
        :return: Список вакансий
        """
        params = {
            "employer_id": employer_id,
            "per_page": per_page,
            "area": 113
        }

        try:
            response = self._session.get(self.__base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except requests.exceptions.RequestException:
            return []