from typing import Dict, List

import requests

from src.api.abstract_api import AbstractAPI


class HeadHunterAPI(AbstractAPI):
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.__base_url = "https://api.hh.ru/vacancies"
        self._connect_to_api()

    def _connect_to_api(self) -> None:
        """Приватный метод для проверки соединения с API"""
        response = requests.get(self.__base_url)
        if response.status_code != 200:
            raise ConnectionError(f"Ошибка подключения к API. Код: {response.status_code}")

    def get_vacancies(self, keyword: str, per_page: int = 100) -> List[Dict]:
        """
        Получение вакансий по ключевому слову
        :param keyword: Ключевое слово для поиска
        :param per_page: Количество результатов на страницу
        :return: Список вакансий
        """
        params = {"text": keyword, "per_page": per_page, "search_field": "name"}
        response = requests.get(self.__base_url, params=params)
        response.raise_for_status()
        return response.json().get("items", [])
