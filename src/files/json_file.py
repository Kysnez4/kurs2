import json
from pathlib import Path
from typing import List, Dict, Any
import logging
from src.files.abstract_file import AbstractFile

class JSONFile(AbstractFile):
    """Класс для работы с JSON-файлами"""

    def __init__(self, filename: str = "data/vacancies.json"):
        self.__filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Создает файл и директорию, если они не существуют"""
        try:
            Path(self.__filename).parent.mkdir(parents=True, exist_ok=True)
            if not Path(self.__filename).exists():
                with open(self.__filename, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
        except (IOError, OSError) as e:
            logging.error(f"Ошибка при создании файла: {e}")
            raise

    def add_vacancy(self, vacancy: Dict[str, Any]) -> None:
        """Добавление вакансии в JSON-файл с проверкой на дубликаты"""
        try:
            existing = self.get_vacancies()

            # Проверяем, что такой вакансии еще нет
            if not any(v == vacancy for v in existing):
                existing.append(vacancy)
                self._save_to_file(existing)
        except Exception as e:
            logging.error(f"Ошибка при добавлении вакансии: {e}")
            raise

    def get_vacancies(self) -> List[Dict[str, Any]]:
        """Получение всех вакансий из JSON-файла"""
        try:
            with open(self.__filename, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():  # Если файл пустой
                    return []
                return json.loads(content)
        except json.JSONDecodeError:
            logging.warning("Файл поврежден, будет создан новый")
            self._save_to_file([])
            return []
        except Exception as e:
            logging.error(f"Ошибка при чтении файла: {e}")
            raise

    def delete_vacancies(self) -> None:
        """Очистка JSON-файла"""
        self._save_to_file([])

    def _save_to_file(self, data: List[Dict[str, Any]]) -> None:
        """Приватный метод для сохранения данных в файл"""
        try:
            with open(self.__filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Ошибка при сохранении в файл: {e}")
            raise