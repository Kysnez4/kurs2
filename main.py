import logging
import os
from src.api.hh_api import HeadHunterAPI
from src.files.json_file import JSONFile
from src.utils.helpers import convert_to_vacancy_objects, filter_vacancies


def setup_logging():
    """Настройка логирования"""
    # Создаем директорию для логов, если ее нет
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Настройка дополнительного логгера
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    log_file_path = os.path.join(log_dir, "main.log")
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


def user_interaction():
    """Функция для взаимодействия с пользователем"""
    logger = logging.getLogger(__name__)
    logger.info("Запуск программы")

    try:
        print("Добро пожаловать в анализатор вакансий!")

        # Получение вакансий
        keyword = input("Введите ключевое слово для поиска вакансий: ")
        hh_api = HeadHunterAPI()
        raw_vacancies = hh_api.get_vacancies(keyword)
        vacancies = convert_to_vacancy_objects(raw_vacancies)

        # Сохранение в файл
        file = JSONFile()
        for vac in vacancies:
            try:
                file.add_vacancy(vac.to_dict())
            except Exception as e:
                logger.error(f"Ошибка при сохранении вакансии: {e}")
                continue

        # Фильтрация
        filter_words = input("Введите ключевые слова для фильтрации вакансий (через пробел): ").split()
        filtered = filter_vacancies(vacancies, filter_words)

        # Сортировка
        sorted_vacancies = sorted(filtered, reverse=True)

        # Вывод результатов
        print(f"\nНайдено вакансий: {len(sorted_vacancies)}")
        for i, vacancy in enumerate(sorted_vacancies[:10], 1):
            print(f"{i}. {vacancy}")

        # Дополнительные действия
        action = input("\nХотите очистить файл с вакансиями? (да/нет): ")
        if action.lower() == "да":
            file.delete_vacancies()
            print("Файл очищен.")

    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        print("Произошла ошибка. Подробности в логе.")
    finally:
        logger.info("Завершение работы программы")


if __name__ == "__main__":
    setup_logging()  # Инициализация логирования
    user_interaction()