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


class AbstractDB(ABC):  # pragma: no cover
    """Абстрактный класс для работы с базой данных"""

    @abstractmethod
    def get_companies_and_vacancies_count(self) -> List[Dict]:
        """получает список всех компаний
        и количество вакансий у каждой компании."""
        pass

    @abstractmethod
    def get_all_vacancies(self) -> List[Dict]:
        """получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        pass

    @abstractmethod
    def get_avg_salary(self) -> float:
        """получает среднюю зарплату по вакансиям"""
        pass

    @abstractmethod
    def get_vacancies_with_higher_salary(self) -> List[Dict]:
        """получает список всех вакансий,
        у которых зарплата выше средней по всем вакансиям"""
        pass

    @abstractmethod
    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict]:
        """получает список всех вакансий,
        в названии которых содержатся переданные в метод слова"""
        pass
