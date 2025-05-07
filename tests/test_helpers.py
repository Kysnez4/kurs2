from src.models.vacancy import Vacancy
from src.utils.helpers import convert_to_vacancy_objects, filter_vacancies


class TestHelpers:
    """Тесты вспомогательных функций"""

    def test_convert_to_vacancy_objects(self):
        """Тест конвертации данных API в объекты Vacancy"""
        api_data = [
            {
                "name": "Python Dev",
                "alternate_url": "http://example.com",
                "salary": {"from": 100000, "to": 150000},
                "snippet": {"requirement": "Python experience"},
                "employer": {"name": "Company"},
            }
        ]

        vacancies = convert_to_vacancy_objects(api_data)

        assert len(vacancies) == 1
        assert isinstance(vacancies[0], Vacancy)
        assert vacancies[0].title == "Python Dev"
        assert vacancies[0].salary_from == 100000

    def test_filter_vacancies(self):
        """Тест фильтрации вакансий"""
        vacancies = [
            Vacancy("Python Developer", "http://example.com", 100000, 150000, "Need Python skills", "Company1"),
            Vacancy("Java Developer", "http://example.com", 90000, 120000, "Java experience required", "Company2"),
            Vacancy("DevOps", "http://example.com", 120000, 180000, "Python and Docker", "Company3"),
        ]

        # Фильтр по Python
        filtered = filter_vacancies(vacancies, ["Python"])
        assert len(filtered) == 2
        assert filtered[0].title == "Python Developer"
        assert filtered[1].title == "DevOps"

        # Без фильтра
        no_filter = filter_vacancies(vacancies, [])
        assert len(no_filter) == 3

        # Фильтр по несуществующему слову
        empty = filter_vacancies(vacancies, ["Ruby"])
        assert len(empty) == 0
