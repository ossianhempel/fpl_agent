from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Engine
import psycopg2
import os
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential


class DatabaseSchema:
    """Object that stores the database schema"""
    def __init__(self):
        pass


@dataclass
class DatabaseConfig:
    db_password: str = os.getenv("PG_PASSWORD", "empty")
    db_name: str = os.getenv("PG_DATABASE", "empty")
    db_user: str = os.getenv("PG_USER", "empty")
    db_port: str = os.getenv("PG_PORT", "empty")
    db_host: str = os.getenv("PG_HOST", "empty")
    gemini_key: str = os.getenv("GEMINI_API_KEY", "empty")

class DatabaseManager:
    def __init__(self):
        self.config = DatabaseConfig()
        self.connection = None
        self.cursor = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _create_connection(self):
        self.connection = psycopg2.connect(
            database=self.config.db_name,
            user=self.config.db_user,
            password=self.config.db_password,
            host=self.config.db_host,
            port=self.config.db_port,
        )
        return self.connection
    
    def _create_cursor(self):
        if self.cursor is None or self.cursor.closed:
            if not self.connection:
                self.connection = self._create_connection()
            self.cursor = self.connection.cursor()
        return self.cursor

    def close(self):
        """close all database connections"""
        if self.cursor:
            self.cursor.close()
        
        if self.connection:
            self.connection.commit()
            self.connection.close()
        
        self.cursor = None
        self.connection = None
        
        print("Database connection closed")
    
    def execute_query(self, query):
        if not self.cursor:
            self.cursor = self._create_cursor()
        
        self.cursor.execute(query)
        result = self.cursor.fetchall()

        return result


    def get_schema(self) -> None:
        if not self.connection:
            self.connection = self._create_connection()
        
        with self.connection.cursor() as cur:
            # query to get schema information
            cur.execute("""
                SELECT
                    table_name,
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_schema = 'dbt_ohempel'
                ORDER BY table_name, ordinal_position;
            """)
            current_table = None
            for table_name, column_name, data_type in cur.fetchall():
                if table_name != current_table:
                    print(f"\nTable: {table_name}")
                    current_table = table_name
                print(f" - {column_name}: {data_type}")






if __name__ == "__main__":
    load_dotenv()

    db_manager = DatabaseManager()
    print("Executing query..")
    
    result = db_manager.execute_query("""
        select * from dbt_ohempel.dim_teams LIMIT 10
        """
    )

    print(result)

    db_manager.get_schema()

    db_manager.close()
