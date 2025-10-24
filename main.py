import logging
import os
from typing import List, Dict

from src.api.hh_api import HeadHunterAPI
from src.files.db_store import DBManager
from src.files.json_file import JSONFile
from src.utils.helpers import convert_to_vacancy_objects, filter_vacancies


def setup_logging():
    """Настройка логирования"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    log_file_path = os.path.join(log_dir, "main.log")
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


def get_db_credentials():
    """Получение данных для подключения к БД от пользователя"""
    print("\n=== Настройка подключения к базе данных ===")
    dbname = input("Имя базы данных: ") or "vacancies_db"
    user = input("Пользователь: ") or "postgres"
    password = input("Пароль: ")
    host = input("Хост (localhost): ") or "localhost"
    return dbname, user, password, host


def load_vacancies_from_companies(hh_api: HeadHunterAPI, db_manager: DBManager) -> List[Dict]:
    """Загружает вакансии от 10 компаний."""
    logger = logging.getLogger(__name__)

    # ID компаний с HH (те же что в _populate_companies)
    company_ids = [1740, 3529, 15478, 2180, 78638, 80, 3776, 39305, 41862, 907345]
    all_vacancies = []

    print("\n=== Загрузка вакансий от компаний ===")

    for company_id in company_ids:
        try:
            print(f"Загрузка вакансий для компании ID: {company_id}")
            vacancies_data = hh_api.get_vacancies_by_employer(str(company_id))

            if vacancies_data:
                # Конвертируем в объекты Vacancy
                company_vacancies = convert_to_vacancy_objects(vacancies_data)

                # Сохраняем в БД
                for vacancy in company_vacancies:
                    try:
                        # Получаем company_id из БД
                        db_company_id = db_manager.get_company_id_by_hh_id(company_id)
                        if db_company_id:
                            vacancy_dict = vacancy.to_dict()
                            vacancy_dict['company_id'] = db_company_id
                            vacancy_dict['hh_id'] = hash(vacancy.url)  # Уникальный ID на основе URL
                            db_manager.add_vacancy(vacancy_dict)
                            all_vacancies.append(vacancy_dict)
                    except Exception as e:
                        logger.error(f"Ошибка при сохранении вакансии: {e}")
                        continue

                print(f"Загружено {len(company_vacancies)} вакансий")
            else:
                print(f"Не найдено вакансий для компании ID: {company_id}")

        except Exception as e:
            logger.error(f"Ошибка при загрузке вакансий компании {company_id}: {e}")
            print(f"Ошибка при загрузке вакансий компании {company_id}")
            continue

    print(f"\nВсего загружено вакансий: {len(all_vacancies)}")
    return all_vacancies


def db_interaction(db_manager: DBManager):
    """Функция для взаимодействия с базой данных"""
    while True:
        print("\n=== Работа с базой данных ===")
        print("1. Получить список компаний и количество вакансий")
        print("2. Получить все вакансии")
        print("3. Получить среднюю зарплату по вакансиям")
        print("4. Получить вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("6. Вернуться в основное меню")

        choice = input("Ваш выбор (1-6): ").strip()

        try:
            if choice == "1":
                companies = db_manager.get_companies_and_vacancies_count()
                print("\n=== Компании и количество вакансий ===")
                for company in companies:
                    print(f"• {company['company']}: {company['vacancies_count']} вакансий")

            elif choice == "2":
                vacancies = db_manager.get_all_vacancies()
                print(f"\n=== Все вакансии ({len(vacancies)}) ===")
                for i, vacancy in enumerate(vacancies, 1):
                    salary_info = ""
                    if vacancy.salary_from or vacancy.salary_to:
                        salary_info = f" | Зарплата: {vacancy.salary_from or '?'} - {vacancy.salary_to or '?'}"
                    print(f"{i}. {vacancy.employer} - {vacancy.title}{salary_info}")
                    print(f"   Ссылка: {vacancy.url}")
                    if i % 5 == 0 and i < len(vacancies):
                        input("Нажмите Enter для продолжения...")

            elif choice == "3":
                avg_salary = db_manager.get_avg_salary()
                print(f"\n=== Средняя зарплата по вакансиям ===")
                print(f"Средняя зарплата: {avg_salary:.2f} руб.")

            elif choice == "4":
                vacancies = db_manager.get_vacancies_with_higher_salary()
                print(f"\n=== Вакансии с зарплатой выше средней ({len(vacancies)}) ===")
                for i, vacancy in enumerate(vacancies, 1):
                    salary_info = f"Зарплата: {vacancy.salary_from or '?'} - {vacancy.salary_to or '?'}"
                    print(f"{i}. {vacancy.employer} - {vacancy.title} | {salary_info}")

            elif choice == "5":
                keyword = input("Введите ключевое слово для поиска: ").strip()
                if keyword:
                    vacancies = db_manager.get_vacancies_with_keyword(keyword)
                    print(f"\n=== Найдено вакансий по запросу '{keyword}' ({len(vacancies)}) ===")
                    for i, vacancy in enumerate(vacancies, 1):
                        salary_info = ""
                        if vacancy.salary_from or vacancy.salary_to:
                            salary_info = f" | Зарплата: {vacancy.salary_from or '?'} - {vacancy.salary_to or '?'}"
                        print(f"{i}. {vacancy.employer} - {vacancy.title}{salary_info}")
                else:
                    print("Ключевое слово не может быть пустым")

            elif choice == "6":
                break

            else:
                print("Неверный выбор. Попробуйте снова.")

        except Exception as e:
            print(f"Произошла ошибка: {e}")


def user_interaction():
    """Основная функция для взаимодействия с пользователем"""
    logger = logging.getLogger(__name__)
    logger.info("Запуск программы")

    try:
        print("=== Добро пожаловать в анализатор вакансий! ===")

        # Получение данных для подключения к БД
        dbname, user, password, host = get_db_credentials()

        print("\nИнициализация базы данных...")
        db_manager = DBManager(dbname, user, password, host)

        # Инициализация API
        hh_api = HeadHunterAPI()

        # Проверка соединения с API
        try:
            hh_api._connect_to_api()
            print("✓ Соединение с API HH.ru установлено")
        except ConnectionError as e:
            print(f"✗ Ошибка соединения с API: {e}")
            return

        # Загрузка вакансий от компаний
        print("\n=== Начало загрузки вакансий ===")
        vacancies_data = load_vacancies_from_companies(hh_api, db_manager)

        if not vacancies_data:
            print("Не удалось загрузить вакансии. Продолжаем работу с существующими данными.")

        # Основное меню
        while True:
            print("\n=== Главное меню ===")
            print("1. Работа с базой данных")
            print("2. Обновить вакансии (очистить и загрузить заново)")
            print("3. Выход")

            main_choice = input("Ваш выбор (1-3): ").strip()

            if main_choice == "1":
                db_interaction(db_manager)
            elif main_choice == "2":
                confirm = input("Вы уверены? Все существующие вакансии будут удалены. (да/нет): ")
                if confirm.lower() == 'да':
                    print("Очистка базы данных...")
                    db_manager.delete_vacancies()
                    print("Загрузка новых вакансий...")
                    load_vacancies_from_companies(hh_api, db_manager)
            elif main_choice == "3":
                print("До свидания!")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        print("Произошла критическая ошибка. Подробности в логе.")
    finally:
        logger.info("Завершение работы программы")


if __name__ == "__main__":
    setup_logging()
    user_interaction()