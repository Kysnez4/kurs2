from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class AbstractAPI(ABC):  # pragma: no cover
    """Абстрактный класс для работы с API вакансий"""

    @abstractmethod
    def _connect_to_api(self):
        """Проверка соединения с API"""
        pass

    @abstractmethod
    def get_vacancies(self, keyword: str, per_page: Optional[int] = None) -> List[Dict]:
        """Получение вакансий по ключевому слову"""
        pass

    @abstractmethod
    def get_vacancies_by_employer(self, employer_id: str, per_page: Optional[int] = None) -> List[Dict]:
        """Получение вакансий по конкретному работодателю"""
        pass