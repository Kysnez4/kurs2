from abc import ABC, abstractmethod
from typing import Dict, List


class AbstractFile(ABC):  # pragma: no cover
    """Абстрактный класс для работы с файлами"""

    @abstractmethod
    def add_vacancy(self, vacancy: Dict) -> None:
        """Добавление вакансии в файл"""
        pass

    @abstractmethod
    def get_vacancies(self) -> List[Dict]:
        """Получение вакансий из файла"""
        pass

    @abstractmethod
    def delete_vacancies(self) -> None:
        """Удаление всех вакансий из файла"""
        pass
