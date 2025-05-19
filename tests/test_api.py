from unittest.mock import Mock, patch

import pytest

from src.api.hh_api import HeadHunterAPI


class TestHeadHunterAPI: # pragma: no cover
    """Тесты для класса HeadHunterAPI"""
    def test_connect(self):
        api = HeadHunterAPI()
        assert '<Response [200]>' == str(api._connect_to_api())


    @patch("requests.get")
    def test_get_vacancies(self, mock_get):
        """Тест получения вакансий"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "name": "Python Developer",
                    "alternate_url": "http://example.com",
                    "salary": {"from": 100000, "to": 150000},
                    "snippet": {"requirement": "Опыт работы с Python"},
                    "employer": {"name": "Test Company"},
                }
            ]
        }
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        vacancies = api.get_vacancies("Python")

        assert len(vacancies) == 1
        assert vacancies[0]["name"] == "Python Developer"
        mock_get.assert_called_with(
            "https://api.hh.ru/vacancies", params={"text": "Python", "per_page": 100, "search_field": "name"}
        )
