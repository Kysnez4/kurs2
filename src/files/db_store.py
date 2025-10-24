import logging
from functools import wraps
from typing import Dict, List
import psycopg2
from src.files.abstract_file import AbstractDB
from src.models.vacancy import Vacancy


def db_connection(func):
    """Декоратор для управления подключением к базе данных."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        conn = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host)
        try:
            with conn.cursor() as cur:
                result = func(self, cur, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    return wrapper


class DBManager(AbstractDB):
    """Класс для работы с базой данных PostgreSQL."""

    def __init__(self, dbname: str, user: str, password: str, host: str):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.create_tables()
        self.populate_companies()

    @db_connection
    def create_tables(self, cur) -> None:
        """Создаёт таблицы компаний и вакансий."""
        # Таблица компаний
        companies_query = """
                          CREATE TABLE IF NOT EXISTS companies \
                          ( \
                              id \
                              SERIAL \
                              PRIMARY \
                              KEY, \
                              name \
                              VARCHAR \
                          ( \
                              255 \
                          ) NOT NULL UNIQUE,
                              description TEXT,
                              website VARCHAR \
                          ( \
                              255 \
                          ),
                              hh_url VARCHAR \
                          ( \
                              255 \
                          )
                              ); \
                          """
        cur.execute(companies_query)

        # Таблица вакансий с внешним ключом
        vacancies_query = """
                          CREATE TABLE IF NOT EXISTS vacancies \
                          ( \
                              id \
                              SERIAL \
                              PRIMARY \
                              KEY, \
                              title \
                              VARCHAR \
                          ( \
                              255 \
                          ) NOT NULL,
                              url VARCHAR \
                          ( \
                              255 \
                          ) NOT NULL,
                              salary_from INT,
                              salary_to INT,
                              description TEXT,
                              company_id INT REFERENCES companies \
                          ( \
                              id \
                          ) ON DELETE CASCADE
                              ); \
                          """
        cur.execute(vacancies_query)

    @db_connection
    def populate_companies(self, cur) -> None:
        """Заполняет таблицу компаний данными."""
        companies = [
            {"name": "Яндекс", "description": "Российская ИТ-компания", "website": "https://yandex.ru",
             "hh_url": "https://hh.ru/employer/1740"},
            {"name": "Сбер", "description": "Крупнейший банк России", "website": "https://sber.ru",
             "hh_url": "https://hh.ru/employer/3529"},
            {"name": "VK", "description": "Технологическая компания", "website": "https://vk.com",
             "hh_url": "https://hh.ru/employer/15478"},
            {"name": "Ozon", "description": "Интернет-магазин", "website": "https://ozon.ru",
             "hh_url": "https://hh.ru/employer/2180"},
            {"name": "Тинькофф", "description": "Тинькофф Банк", "website": "https://tinkoff.ru",
             "hh_url": "https://hh.ru/employer/78638"},
            {"name": "Альфа-Банк", "description": "Крупный частный банк", "website": "https://alfabank.ru",
             "hh_url": "https://hh.ru/employer/80"},
            {"name": "МТС", "description": "Телекоммуникационная компания", "website": "https://mts.ru",
             "hh_url": "https://hh.ru/employer/3776"},
            {"name": "Газпром", "description": "Энергетическая компания", "website": "https://gazprom.ru",
             "hh_url": "https://hh.ru/employer/39305"},
            {"name": "Ростелеком", "description": "Телекоммуникационная компания", "website": "https://rt.ru",
             "hh_url": "https://hh.ru/employer/41862"},
            {"name": "Лукойл", "description": "Нефтяная компания", "website": "https://lukoil.ru",
             "hh_url": "https://hh.ru/employer/907345"}
        ]

        for company in companies:
            query = """
                    INSERT INTO companies (name, description, website, hh_url)
                    VALUES (%s, %s, %s, %s) ON CONFLICT (name) DO NOTHING; \
                    """
            cur.execute(query, (company["name"], company["description"], company["website"], company["hh_url"]))

    @db_connection
    def add_vacancy(self, cur, vacancy: Dict) -> None:
        """Добавляет вакансию в таблицу vacancies."""
        try:
            # Получаем ID компании
            company_query = "SELECT id FROM companies WHERE name = %s;"
            cur.execute(company_query, (vacancy['employer'],))
            company_result = cur.fetchone()

            if not company_result:
                # Если компании нет в базе, создаем её
                company_insert = """
                                 INSERT INTO companies (name)
                                 VALUES (%s) RETURNING id; \
                                 """
                cur.execute(company_insert, (vacancy['employer'],))
                company_result = cur.fetchone()

            company_id = company_result[0]

            # Очистка строковых полей от проблемных символов
            cleaned_vacancy = {
                'title': vacancy['title'].encode('utf-8', 'ignore').decode('utf-8') if vacancy['title'] else '',
                'url': vacancy['url'],
                'salary_from': vacancy['salary_from'],
                'salary_to': vacancy['salary_to'],
                'description': vacancy['description'].encode('utf-8', 'ignore').decode('utf-8') if vacancy[
                    'description'] else '',
            }

            query = """
                    INSERT INTO vacancies (title, url, salary_from, salary_to, description, company_id)
                    VALUES (%s, %s, %s, %s, %s, %s) \
                    """
            cur.execute(query, (
                cleaned_vacancy['title'],
                cleaned_vacancy['url'],
                cleaned_vacancy['salary_from'],
                cleaned_vacancy['salary_to'],
                cleaned_vacancy['description'],
                company_id
            ))
        except Exception as e:
            logging.error(f"Ошибка при добавлении вакансии: {e}")
            raise

    @db_connection
    def get_companies_and_vacancies_count(self, cur) -> List[Dict]:
        """Получает список компаний и количество их вакансий с использованием JOIN."""
        query = """
                SELECT c.name, COUNT(v.id) as vacancies_count
                FROM companies c
                         LEFT JOIN vacancies v ON c.id = v.company_id
                GROUP BY c.id, c.name
                ORDER BY vacancies_count DESC; \
                """
        cur.execute(query)
        result = cur.fetchall()
        return [{"company": row[0], "vacancies_count": row[1]} for row in result]

    @db_connection
    def get_all_vacancies(self, cur) -> List[Vacancy]:
        """Получает список всех вакансий в виде объектов Vacancy с использованием JOIN."""
        query = """
                SELECT v.title, v.url, v.salary_from, v.salary_to, v.description, c.name
                FROM vacancies v
                         JOIN companies c ON v.company_id = c.id; \
                """
        cur.execute(query)
        result = cur.fetchall()
        return [Vacancy.from_db_row(row) for row in result]

    @db_connection
    def get_avg_salary(self, cur) -> float:
        """Вычисляет среднюю зарплату по вакансиям."""
        query = """
                SELECT AVG((salary_from + salary_to) / 2) as avg_salary
                FROM vacancies
                WHERE salary_from IS NOT NULL \
                  AND salary_to IS NOT NULL; \
                """
        cur.execute(query)
        result = cur.fetchone()
        return float(result[0]) if result[0] else 0.0

    @db_connection
    def get_vacancies_with_higher_salary(self, cur) -> List[Vacancy]:
        """Получает вакансии с зарплатой выше средней."""
        avg_salary = self.get_avg_salary()
        query = """
                SELECT v.title, v.url, v.salary_from, v.salary_to, v.description, c.name
                FROM vacancies v
                         JOIN companies c ON v.company_id = c.id
                WHERE ((v.salary_from + v.salary_to) / 2) > %s; \
                """
        cur.execute(query, (avg_salary,))
        result = cur.fetchall()
        return [Vacancy.from_db_row(row) for row in result]

    @db_connection
    def get_vacancies_with_keyword(self, cur, keyword: str) -> List[Vacancy]:
        """Ищет вакансии по ключевому слову в названии."""
        query = """
                SELECT v.title, v.url, v.salary_from, v.salary_to, v.description, c.name
                FROM vacancies v
                         JOIN companies c ON v.company_id = c.id
                WHERE v.title ILIKE %s; \
                """
        cur.execute(query, (f"%{keyword}%",))
        result = cur.fetchall()
        return [Vacancy.from_db_row(row) for row in result]

    @db_connection
    def delete_vacancies(self, cur) -> None:
        """Удаляет все вакансии."""
        query = "TRUNCATE TABLE vacancies RESTART IDENTITY;"
        cur.execute(query)

    @db_connection
    def get_company_by_name(self, cur, company_name: str) -> Dict:
        """Получает информацию о компании по имени."""
        query = "SELECT * FROM companies WHERE name = %s;"
        cur.execute(query, (company_name,))
        result = cur.fetchone()
        if result:
            return {
                "id": result[0],
                "name": result[1],
                "description": result[2],
                "website": result[3],
                "hh_url": result[4]
            }
        return {}