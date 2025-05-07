from abc import ABC, abstractmethod
from typing import Dict, List


class AbstractAPI(ABC):  # pragma: no cover
    """Абстрактный класс для работы с API вакансий"""

    @abstractmethod
    def _connect_to_api(self) -> None:
        """Установка соединения с API"""
        pass

    @abstractmethod
    def get_vacancies(self, keyword: str) -> List[Dict]:
        """Получение вакансий по ключевому слову"""
        pass
