import logging
from functools import wraps
from typing import Dict, List, Optional
import psycopg2
from src.files.abstract_file import AbstractDB
from src.models.vacancy import Vacancy


def db_connection(func):
    """Декоратор для управления подключением к базе данных."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host
        )
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
        self._create_database()
        self.create_tables()
        self._populate_companies()

    @db_connection
    def _create_database(self, cur=None) -> None:
        """Создание базы данных если не существует."""
        # Подключаемся к базе данных postgres для создания новой БД
        conn = psycopg2.connect(
            dbname="postgres",
            user=self.user,
            password=self.password,
            host=self.host
        )
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.dbname}'")
                exists = cur.fetchone()
                if not exists:
                    cur.execute(f"CREATE DATABASE {self.dbname}")
        finally:
            conn.close()

    @db_connection
    def create_tables(self, cur) -> None:
        """Создаёт таблицы компаний и вакансий."""
        # Таблица компаний
        companies_query = """
                          CREATE TABLE IF NOT EXISTS companies \
                          ( \
                              company_id \
                              SERIAL \
                              PRIMARY \
                              KEY, \
                              hh_id \
                              INTEGER \
                              UNIQUE \
                              NOT \
                              NULL, \
                              name \
                              VARCHAR \
                          ( \
                              255 \
                          ) NOT NULL,
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
                              vacancy_id \
                              SERIAL \
                              PRIMARY \
                              KEY, \
                              hh_id \
                              INTEGER \
                              UNIQUE \
                              NOT \
                              NULL, \
                              title \
                              VARCHAR \
                          ( \
                              500 \
                          ) NOT NULL,
                              url VARCHAR \
                          ( \
                              255 \
                          ) NOT NULL,
                              salary_from INTEGER,
                              salary_to INTEGER,
                              currency VARCHAR \
                          ( \
                              10 \
                          ),
                              description TEXT,
                              company_id INTEGER REFERENCES companies \
                          ( \
                              company_id \
                          ) ON DELETE CASCADE,
                              created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                              ); \
                          """
        cur.execute(vacancies_query)

    @db_connection
    def _populate_companies(self, cur) -> None:
        """Заполняет таблицу компаний 10 компаниями."""
        companies = [
            {
                "hh_id": 1740,
                "name": "Яндекс",
                "description": "Российская транснациональная компания в отрасли интернет-поиска и технологий",
                "website": "https://yandex.ru",
                "hh_url": "https://hh.ru/employer/1740"
            },
            {
                "hh_id": 3529,
                "name": "Сбер",
                "description": "Крупнейший банк России и один из ведущих финансовых конгломератов Центральной и Восточной Европы",
                "website": "https://sber.ru",
                "hh_url": "https://hh.ru/employer/3529"
            },
            {
                "hh_id": 15478,
                "name": "VK",
                "description": "Российская технологическая компания, владелец одноимённой социальной сети",
                "website": "https://vk.com",
                "hh_url": "https://hh.ru/employer/15478"
            },
            {
                "hh_id": 2180,
                "name": "Ozon",
                "description": "Российская компания, владеющая одноимённой интернет-платформой",
                "website": "https://ozon.ru",
                "hh_url": "https://hh.ru/employer/2180"
            },
            {
                "hh_id": 78638,
                "name": "Тинькофф",
                "description": "Российский финтех-банк, предоставляющий финансовые услуги",
                "website": "https://tinkoff.ru",
                "hh_url": "https://hh.ru/employer/78638"
            },
            {
                "hh_id": 80,
                "name": "Альфа-Банк",
                "description": "Крупнейший частный банк России",
                "website": "https://alfabank.ru",
                "hh_url": "https://hh.ru/employer/80"
            },
            {
                "hh_id": 3776,
                "name": "МТС",
                "description": "Российская телекоммуникационная компания",
                "website": "https://mts.ru",
                "hh_url": "https://hh.ru/employer/3776"
            },
            {
                "hh_id": 39305,
                "name": "Газпром",
                "description": "Российская энергетическая компания",
                "website": "https://gazprom.ru",
                "hh_url": "https://hh.ru/employer/39305"
            },
            {
                "hh_id": 41862,
                "name": "Ростелеком",
                "description": "Российская телекоммуникационная компания",
                "website": "https://rt.ru",
                "hh_url": "https://hh.ru/employer/41862"
            },
            {
                "hh_id": 907345,
                "name": "Лукойл",
                "description": "Российская нефтяная компания",
                "website": "https://lukoil.ru",
                "hh_url": "https://hh.ru/employer/907345"
            }
        ]

        for company in companies:
            query = """
                    INSERT INTO companies (hh_id, name, description, website, hh_url)
                    VALUES (%s, %s, %s, %s, %s) ON CONFLICT (hh_id) DO NOTHING; \
                    """
            cur.execute(query, (
                company["hh_id"],
                company["name"],
                company["description"],
                company["website"],
                company["hh_url"]
            ))

    @db_connection
    def add_vacancy(self, cur, vacancy: Dict) -> None:
        """Добавляет вакансию в таблицу vacancies."""
        try:
            query = """
                    INSERT INTO vacancies (hh_id, title, url, salary_from, salary_to, currency, description, company_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (hh_id) DO NOTHING; \
                    """
            cur.execute(query, (
                vacancy['hh_id'],
                vacancy['title'],
                vacancy['url'],
                vacancy['salary_from'],
                vacancy['salary_to'],
                vacancy['currency'],
                vacancy['description'],
                vacancy['company_id']
            ))
        except Exception as e:
            logging.error(f"Ошибка при добавлении вакансии: {e}")
            raise

    @db_connection
    def get_companies_and_vacancies_count(self, cur) -> List[Dict]:
        """Получает список всех компаний и количество вакансий у каждой компании."""
        query = """
                SELECT c.name, COUNT(v.vacancy_id) as vacancies_count
                FROM companies c
                         LEFT JOIN vacancies v ON c.company_id = v.company_id
                GROUP BY c.company_id, c.name
                ORDER BY vacancies_count DESC; \
                """
        cur.execute(query)
        result = cur.fetchall()
        return [{"company": row[0], "vacancies_count": row[1]} for row in result]

    @db_connection
    def get_all_vacancies(self, cur) -> List[Vacancy]:
        """Получает список всех вакансий с указанием названия компании, вакансии, зарплаты и ссылки."""
        query = """
                SELECT c.name as employer, \
                       v.title, \
                       v.salary_from, \
                       v.salary_to, \
                       v.currency, \
                       v.url, \
                       v.description
                FROM vacancies v
                         JOIN companies c ON v.company_id = c.company_id
                ORDER BY v.salary_from DESC NULLS LAST; \
                """
        cur.execute(query)
        result = cur.fetchall()

        vacancies = []
        for row in result:
            # Создаем объект Vacancy из данных JOIN запроса
            vacancy = Vacancy(
                title=row[1],
                url=row[5],
                salary_from=row[2],
                salary_to=row[3],
                description=row[6],
                employer=row[0]
            )
            vacancies.append(vacancy)

        return vacancies

    @db_connection
    def get_avg_salary(self, cur) -> float:
        """Получает среднюю зарплату по вакансиям."""
        query = """
                SELECT AVG(
                               CASE
                                   WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL \
                                       THEN (salary_from + salary_to) / 2
                                   WHEN salary_from IS NOT NULL THEN salary_from
                                   WHEN salary_to IS NOT NULL THEN salary_to
                                   ELSE NULL
                                   END
                       ) as avg_salary
                FROM vacancies
                WHERE salary_from IS NOT NULL \
                   OR salary_to IS NOT NULL; \
                """
        cur.execute(query)
        result = cur.fetchone()
        return float(result[0]) if result[0] else 0.0

    @db_connection
    def get_vacancies_with_higher_salary(self, cur) -> List[Vacancy]:
        """Получает вакансии с зарплатой выше средней."""
        avg_salary = self.get_avg_salary()
        query = """
                SELECT c.name as employer, \
                       v.title, \
                       v.salary_from, \
                       v.salary_to, \
                       v.currency, \
                       v.url, \
                       v.description
                FROM vacancies v
                         JOIN companies c ON v.company_id = c.company_id
                WHERE (
                          CASE
                              WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN (salary_from + salary_to) / 2
                              WHEN salary_from IS NOT NULL THEN salary_from
                              WHEN salary_to IS NOT NULL THEN salary_to
                              ELSE 0
                              END
                          ) > %s
                ORDER BY v.salary_from DESC NULLS LAST; \
                """
        cur.execute(query, (avg_salary,))
        result = cur.fetchall()

        vacancies = []
        for row in result:
            vacancy = Vacancy(
                title=row[1],
                url=row[5],
                salary_from=row[2],
                salary_to=row[3],
                description=row[6],
                employer=row[0]
            )
            vacancies.append(vacancy)

        return vacancies

    @db_connection
    def get_vacancies_with_keyword(self, cur, keyword: str) -> List[Vacancy]:
        """Ищет вакансии по ключевому слову в названии."""
        query = """
                SELECT c.name as employer, \
                       v.title, \
                       v.salary_from, \
                       v.salary_to, \
                       v.currency, \
                       v.url, \
                       v.description
                FROM vacancies v
                         JOIN companies c ON v.company_id = c.company_id
                WHERE v.title ILIKE %s
                ORDER BY v.salary_from DESC NULLS LAST; \
                """
        cur.execute(query, (f"%{keyword}%",))
        result = cur.fetchall()

        vacancies = []
        for row in result:
            vacancy = Vacancy(
                title=row[1],
                url=row[5],
                salary_from=row[2],
                salary_to=row[3],
                description=row[6],
                employer=row[0]
            )
            vacancies.append(vacancy)

        return vacancies

    @db_connection
    def get_company_id_by_hh_id(self, cur, hh_id: int) -> Optional[int]:
        """Получает ID компании по HH ID."""
        query = "SELECT company_id FROM companies WHERE hh_id = %s;"
        cur.execute(query, (hh_id,))
        result = cur.fetchone()
        return result[0] if result else None

    @db_connection
    def delete_vacancies(self, cur) -> None:
        """Удаляет все вакансии."""
        query = "TRUNCATE TABLE vacancies RESTART IDENTITY;"
        cur.execute(query)