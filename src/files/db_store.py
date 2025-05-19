import logging
from functools import wraps # pragma: no cover
from typing import Dict, List # pragma: no cover
import psycopg2 # pragma: no cover
from src.files.abstract_file import AbstractDB # pragma: no cover
from src.models.vacancy import Vacancy # pragma: no cover


def db_connection(func): # pragma: no cover
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


class DBManager(AbstractDB): # pragma: no cover
    """Класс для работы с базой данных PostgreSQL."""

    def __init__(self, dbname: str, user: str, password: str, host: str):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.create_table()

    @db_connection
    def add_vacancy(self, cur, vacancy: Dict) -> None:
        """Добавляет вакансию в таблицу vacancies."""
        try:
            # Очистка строковых полей от проблемных символов
            cleaned_vacancy = {
                'title': vacancy['title'].encode('utf-8', 'ignore').decode('utf-8') if vacancy['title'] else '',
                'url': vacancy['url'],
                'salary_from': vacancy['salary_from'],
                'salary_to': vacancy['salary_to'],
                'description': vacancy['description'].encode('utf-8', 'ignore').decode('utf-8') if vacancy[
                    'description'] else '',
                'employer': vacancy['employer'].encode('utf-8', 'ignore').decode('utf-8') if vacancy['employer'] else ''
            }

            query = """
                INSERT INTO vacancies (title, url, salary_from, salary_to, description, employer)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(query, (
                cleaned_vacancy['title'],
                cleaned_vacancy['url'],
                cleaned_vacancy['salary_from'],
                cleaned_vacancy['salary_to'],
                cleaned_vacancy['description'],
                cleaned_vacancy['employer']
            ))
        except Exception as e:
            logging.error(f"Ошибка при добавлении вакансии: {e}")
            raise

    @db_connection
    def create_table(self, cur) -> None:
        """Создаёт таблицу"""
        query = """
            CREATE TABLE IF NOT EXISTS vacancies (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    url VARCHAR(255) NOT NULL,
                    salary_from INT,
                    salary_to INT,
                    description TEXT,
                    employer VARCHAR(255) NOT NULL
                );
        """
        cur.execute(query)

    @db_connection
    def get_companies_and_vacancies_count(self, cur) -> List[Dict]:
        """Получает список компаний и количество их вакансий."""
        query = """
                SELECT employer, COUNT(*) as vacancies_count
                FROM vacancies
                GROUP BY employer
                ORDER BY vacancies_count DESC;
            """
        cur.execute(query)
        result = cur.fetchall()
        return [{"company": row[0], "vacancies_count": row[1]} for row in result]

    @db_connection
    def get_all_vacancies(self, cur) -> List[Vacancy]:
        """Получает список всех вакансий в виде объектов Vacancy."""
        query = """
                SELECT title, url, salary_from, salary_to, description, employer
                FROM vacancies;
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
                WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL;
            """
        cur.execute(query)
        result = cur.fetchone()
        return float(result[0]) if result[0] else 0.0

    @db_connection
    def get_vacancies_with_higher_salary(self, cur) -> List[Vacancy]:
        """Получает вакансии с зарплатой выше средней."""
        avg_salary = self.get_avg_salary()
        query = """
                SELECT title, url, salary_from, salary_to, description, employer
                FROM vacancies
                WHERE ((salary_from + salary_to) / 2) > %s;
            """
        cur.execute(query, (avg_salary,))
        result = cur.fetchall()
        return [Vacancy.from_db_row(row) for row in result]

    @db_connection
    def get_vacancies_with_keyword(self, cur, keyword: str) -> List[Vacancy]:
        """Ищет вакансии по ключевому слову в названии."""
        query = """
                SELECT title, url, salary_from, salary_to, description, employer
                FROM vacancies
                WHERE title ILIKE %s;
            """
        cur.execute(query, (f"%{keyword}%",))
        result = cur.fetchall()
        return [Vacancy.from_db_row(row) for row in result]

    @db_connection
    def delete_vacancy(self, cur) -> None:
        """Удаляет вакансию по ID."""
        query = "TRUNCATE TABLE vacancies RESTART IDENTITY;"
        cur.execute(query)

