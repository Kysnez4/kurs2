from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Vacancy:
    """Класс для представления вакансии"""

    __slots__ = ["title", "url", "salary_from", "salary_to", "description", "employer"]

    title: str
    url: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    description: Optional[str]
    employer: str

    def __post_init__(self):
        self._validate_data()

    def _validate_data(self) -> None:
        """Приватный метод валидации данных"""
        if not isinstance(self.title, str):
            raise ValueError("Название вакансии должно быть строкой")
        if not isinstance(self.url, str) or not self.url.startswith("http"):
            raise ValueError("URL должен быть валидной ссылкой")

    def to_dict(self) -> Dict:
        """Преобразование объекта Vacancy в словарь"""
        return {
            "title": self.title,
            "url": self.url,
            "salary_from": self.salary_from,
            "salary_to": self.salary_to,
            "description": self.description,
            "employer": self.employer,
        }

    def __lt__(self, other: "Vacancy") -> bool:
        """Сравнение вакансий по минимальной зарплате"""
        return (self.salary_from or 0) < (other.salary_from or 0)

    def __gt__(self, other: "Vacancy") -> bool:
        """Сравнение вакансий по максимальной зарплате"""
        return (self.salary_to or 0) > (other.salary_to or 0)

    def __str__(self) -> str:
        salary_info = ""
        if self.salary_from or self.salary_to:
            salary_info = f"Зарплата: {self.salary_from or 'не указана'} - {self.salary_to or 'не указана'}"
        return (
            f"Вакансия: {self.title}\n"
            f"Компания: {self.employer}\n"
            f"{salary_info}\n"
            f"Описание: {self.description[:100]}...\n"
            f"Ссылка: {self.url}\n"
        )
