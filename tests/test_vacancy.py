import pytest

from src.models.vacancy import Vacancy


class TestVacancy:
    """Тесты для класса Vacancy"""

    def test_vacancy_creation_valid(self):
        """Тест создания вакансии с валидными данными"""
        vacancy = Vacancy(
            title="Python Developer",
            url="https://example.com",
            salary_from=100000,
            salary_to=150000,
            description="Разработка на Python",
            employer="Test Company",
        )

        assert vacancy.title == "Python Developer"
        assert vacancy.url == "https://example.com"
        assert vacancy.salary_from == 100000
        assert vacancy.salary_to == 150000

    def test_vacancy_creation_invalid(self):
        """Тест создания вакансии с невалидными данными"""
        with pytest.raises(ValueError):
            Vacancy(title=123, url="invalid", salary_from=None, salary_to=None, description="", employer="")

        with pytest.raises(ValueError):
            Vacancy(title="Valid", url="not_a_url", salary_from=None, salary_to=None, description="", employer="")

    def test_vacancy_comparison(self):
        """Тест сравнения вакансий"""
        v1 = Vacancy("Junior", "http://example.com", 50000, 70000, "", "")
        v2 = Vacancy("Middle", "http://example.com", 80000, 100000, "", "")
        v3 = Vacancy("Senior", "http://example.com", 120000, 150000, "", "")

        assert v1 < v2
        assert v2 < v3
        assert v3 > v1
        assert not v1 > v2

    def test_vacancy_str_representation(self):
        """Тест строкового представления вакансии"""
        vacancy = Vacancy(
            title="Dev",
            url="http://example.com",
            salary_from=100000,
            salary_to=None,
            description="Test description",
            employer="Company",
        )

        result = str(vacancy)
        assert "Вакансия: Dev" in result
        assert "Компания: Company" in result
        assert "Зарплата: 100000 - не указана" in result
        assert "Test description" in result

    def test_to_dict_method(self):
        """Тест метода преобразования в словарь"""
        vacancy = Vacancy(
            title="Python Dev",
            url="http://example.com",
            salary_from=100000,
            salary_to=150000,
            description="Python experience",
            employer="Test Company",
        )

        result = vacancy.to_dict()

        assert isinstance(result, dict)
        assert result["title"] == "Python Dev"
        assert result["salary_from"] == 100000
        assert result["employer"] == "Test Company"
