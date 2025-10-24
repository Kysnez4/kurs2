import logging
import os

from src.api.hh_api import HeadHunterAPI
from src.files.db_store import DBManager
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


def get_db_credentials():
    """Получение данных для подключения к БД от пользователя"""
    print("\nДля работы с базой данных необходимо ввести данные для подключения:")
    dbname = input("Имя базы данных: ")
    user = input("Пользователь: ")
    password = input("Пароль: ")
    host = input("Хост (localhost): ") or "localhost"
    return dbname, user, password, host


def db_interaction(db_manager: DBManager):
    """Функция для взаимодействия с базой данных"""
    while True:
        print("\nВыберите действие с базой данных:")
        print("1. Получить список компаний и количество вакансий")
        print("2. Получить все вакансии")
        print("3. Получить среднюю зарплату по вакансиям")
        print("4. Получить вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("6. Вернуться в основное меню")

        choice = input("Ваш выбор: ")

        try:
            if choice == "1":
                companies = db_manager.get_companies_and_vacancies_count()
                print("\nКомпании и количество вакансий:")
                for company in companies:
                    print(f"{company['company']}: {company['vacancies_count']} вакансий")

            elif choice == "2":
                vacancies = db_manager.get_all_vacancies()
                print(f"\nВсе вакансии ({len(vacancies)}):")
                for i, vacancy in enumerate(vacancies, 1):
                    print(f"{i}. {vacancy}")

            elif choice == "3":
                avg_salary = db_manager.get_avg_salary()
                print(f"\nСредняя зарплата по вакансиям: {avg_salary:.2f}")

            elif choice == "4":
                vacancies = db_manager.get_vacancies_with_higher_salary()
                print(f"\nВакансии с зарплатой выше средней ({len(vacancies)}):")
                for i, vacancy in enumerate(vacancies, 1):
                    print(f"{i}. {vacancy}")

            elif choice == "5":
                keyword = input("Введите ключевое слово для поиска: ")
                vacancies = db_manager.get_vacancies_with_keyword(keyword)
                print(f"\nНайдено вакансий ({len(vacancies)}):")
                for i, vacancy in enumerate(vacancies, 1):
                    print(f"{i}. {vacancy}")

            elif choice == "6":
                break

            else:
                print("Неверный выбор. Попробуйте снова.")

        except Exception as e:
            print(f"Произошла ошибка: {e}")


def user_interaction():
    """Функция для взаимодействия с пользователем"""
    logger = logging.getLogger(__name__)
    logger.info("Запуск программы")

    try:
        print("Добро пожаловать в анализатор вакансий!")

        # Получение данных для подключения к БД
        dbname, user, password, host = get_db_credentials()
        db_manager = DBManager(dbname, user, password, host)

        # Получение вакансий
        keyword = input("\nВведите ключевое слово для поиска вакансий: ")
        hh_api = HeadHunterAPI()

        # Проверка соединения с API
        try:
            hh_api._connect_to_api()
            print("Соединение с API установлено успешно")
        except ConnectionError as e:
            print(f"Ошибка соединения с API: {e}")
            return

        raw_vacancies = hh_api.get_vacancies(keyword)
        vacancies = convert_to_vacancy_objects(raw_vacancies)

        # Сохранение в базу данных
        print(f"\nСохранение {len(vacancies)} вакансий в базу данных...")
        for vacancy in vacancies:
            try:
                db_manager.add_vacancy(vacancy.to_dict())
            except Exception as e:
                logger.error(f"Ошибка при сохранении вакансии в БД: {e}")
                continue

        # Фильтрация
        filter_words = input("\nВведите ключевые слова для фильтрации вакансий (через пробел): ").split()
        filtered = filter_vacancies(vacancies, filter_words)

        # Сортировка
        sorted_vacancies = sorted(filtered, reverse=True)

        # Вывод результатов
        print(f"\nНайдено вакансий после фильтрации: {len(sorted_vacancies)}")
        for i, vacancy in enumerate(sorted_vacancies[:10], 1):
            print(f"{i}. {vacancy}")

        # Предложение сохранить в файл
        save_to_file = input("\nХотите сохранить вакансии в файл? (да/нет): ")
        if save_to_file.lower() == "да":
            file = JSONFile()
            for vacancy in sorted_vacancies:
                try:
                    file.add_vacancy(vacancy.to_dict())
                except Exception as e:
                    logger.error(f"Ошибка при сохранении вакансии в файл: {e}")
                    continue
            print("Вакансии сохранены в файл.")

        # Работа с базой данных
        db_interaction(db_manager)

        # Очистка базы данных
        clear_db = input("\nХотите очистить базу данных от вакансий? (да/нет): ")
        if clear_db.lower() == "да":
            db_manager.delete_vacancies()
            print("База данных очищена.")

    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        print("Произошла ошибка. Подробности в логе.")
    finally:
        logger.info("Завершение работы программы")


if __name__ == "__main__":
    setup_logging()  # Инициализация логирования
    user_interaction()