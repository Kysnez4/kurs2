import json
import os
from unittest.mock import patch

import pytest

from src.files.json_file import JSONFile


class TestJSONFile:
    """Тесты для класса JSONFile"""

    TEST_FILE = "tests/test_vacancies.json"

    def setup_method(self):
        """Подготовка тестового окружения"""
        if os.path.exists(self.TEST_FILE):
            os.remove(self.TEST_FILE)

    def teardown_method(self):
        """Очистка после тестов"""
        if os.path.exists(self.TEST_FILE):
            os.remove(self.TEST_FILE)

    def test_file_initialization_creates_file(self):
        """Тест автоматического создания файла при инициализации"""
        assert not os.path.exists(self.TEST_FILE)
        JSONFile(self.TEST_FILE)
        assert os.path.exists(self.TEST_FILE)

        with open(self.TEST_FILE, "r") as f:
            content = json.load(f)
            assert content == []

    def test_add_vacancy(self):
        """Тест добавления вакансии"""
        json_file = JSONFile(self.TEST_FILE)
        test_vacancy = {"title": "Test", "url": "http://example.com"}

        json_file.add_vacancy(test_vacancy)

        with open(self.TEST_FILE, "r") as f:
            content = json.load(f)
            assert len(content) == 1
            assert content[0]["title"] == "Test"

    def test_add_duplicate_vacancy(self):
        """Тест добавления дубликата вакансии"""
        json_file = JSONFile(self.TEST_FILE)
        test_vacancy = {"title": "Test", "url": "http://example.com"}

        json_file.add_vacancy(test_vacancy)
        json_file.add_vacancy(test_vacancy)  # Дубликат

        with open(self.TEST_FILE, "r") as f:
            content = json.load(f)
            assert len(content) == 1  # Дубликат не добавлен

    def test_get_vacancies_empty_file(self):
        """Тест получения вакансий из пустого файла"""
        json_file = JSONFile(self.TEST_FILE)
        assert json_file.get_vacancies() == []

    def test_get_vacancies_with_data(self):
        """Тест получения вакансий из файла с данными"""
        test_data = [{"title": "Test1"}, {"title": "Test2"}]
        with open(self.TEST_FILE, "w") as f:
            json.dump(test_data, f)

        json_file = JSONFile(self.TEST_FILE)
        result = json_file.get_vacancies()
        assert len(result) == 2
        assert result[0]["title"] == "Test1"

    def test_delete_vacancies(self):
        """Тест очистки файла"""
        test_data = [{"title": "Test1"}]
        with open(self.TEST_FILE, "w") as f:
            json.dump(test_data, f)

        json_file = JSONFile(self.TEST_FILE)
        json_file.delete_vacancies()

        with open(self.TEST_FILE, "r") as f:
            content = json.load(f)
            assert content == []

    def test_corrupted_file_handling(self):
        """Тест обработки поврежденного файла"""
        # Создаем поврежденный JSON файл
        with open(self.TEST_FILE, "w") as f:
            f.write("{invalid json}")

        json_file = JSONFile(self.TEST_FILE)
        result = json_file.get_vacancies()  # Должен восстановить файл

        assert result == []
        with open(self.TEST_FILE, "r") as f:
            content = json.load(f)
            assert content == []  # Файл должен быть восстановлен

    @patch("builtins.open", side_effect=IOError("Simulated IO error"))
    def test_file_io_error_handling(self, mock_file):
        """Тест обработки ошибок ввода-вывода"""
        with pytest.raises(IOError):
            JSONFile(self.TEST_FILE)

    def test_directory_creation(self):
        """Тест автоматического создания директории"""
        nested_file = "test_dir/nested/vacancies.json"
        import shutil

        if os.path.exists("test_dir"):

            shutil.rmtree("test_dir")

        assert not os.path.exists("test_dir")
        JSONFile(nested_file)
        assert os.path.exists("test_dir/nested")

        # Очистка
        shutil.rmtree("test_dir")

    def test_unicode_handling(self):
        """Тест обработки unicode-символов"""
        json_file = JSONFile(self.TEST_FILE)
        test_vacancy = {"title": "Тест", "description": "Описание с русскими символами"}

        json_file.add_vacancy(test_vacancy)

        with open(self.TEST_FILE, "r", encoding="utf-8") as f:
            content = json.load(f)
            assert content[0]["title"] == "Тест"
            assert "русскими" in content[0]["description"]

    def test_multiple_instances(self):
        """Тест работы с несколькими экземплярами класса"""
        json_file1 = JSONFile(self.TEST_FILE)
        json_file1.add_vacancy({"title": "Test1"})

        json_file2 = JSONFile(self.TEST_FILE)
        json_file2.add_vacancy({"title": "Test2"})

        assert len(json_file1.get_vacancies()) == 2
        assert len(json_file2.get_vacancies()) == 2
