import mysql.connector
import pandas as pd
from contextlib import contextmanager


class DatabaseOperations:
    def __init__(self, host="localhost", port=3306, user="root", password="kasia", database_name="destination"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database_name = database_name

    @contextmanager
    def _get_connection(self):
        """Context manager to handle database connection and cursor."""
        conn = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database_name,
            charset='utf-8',
            collation='utf8mb4_unicode_ci'
        )
        try:
            cur = conn.cursor()
            yield cur, conn
        finally:
            cur.close()
            conn.close()

    def select_from_db(self, table_name, columns=None):
        columns_str = ", ".join([f"`{col}`" for col in columns]) if columns else "*"
        query = f"SELECT {columns_str} FROM {table_name};"

        with self._get_connection() as (cur, conn):
            cur.execute(query)
            rows = cur.fetchall()
            col_names = [desc[0] for desc in cur.description]

        return pd.DataFrame(rows, columns=col_names)

    def add_to_database(self, df, table_name):
        columns_str = ", ".join(df.columns)
        placeholders = ", ".join(["%s"] * len(df.columns))
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

        with self._get_connection() as (cur, conn):
            for _, row in df.iterrows():
                cur.execute(query, tuple(row))
            conn.commit()

    def initialize_cache_db(self):
        query = '''
            CREATE TABLE IF NOT EXISTS flights_cache (
                id INT AUTO_INCREMENT PRIMARY KEY,
                region VARCHAR(255),
                date1 DATE,
                date2 DATE,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        '''
        with self._get_connection() as (cur, conn):
            cur.execute(query)
            conn.commit()

    def get_cached_response(self, region, date1, date2):
        query = '''
            SELECT response FROM flights_cache 
            WHERE region = %s AND date1 = %s AND date2 = %s
        '''
        with self._get_connection() as (cur, conn):
            cur.execute(query, (region, date1, date2))
            rows = cur.fetchall()

        if rows:
            dataframes = [pd.read_json(row[0]) for row in rows]
            return pd.concat(dataframes, ignore_index=True)
        return None

    def cache_response(self, region, date1, date2, response):
        query = '''
            INSERT INTO flights_cache (region, date1, date2, response)
            VALUES (%s, %s, %s, %s)
        '''
        with self._get_connection() as (cur, conn):
            cur.execute(query, (region, date1, date2, response))
            conn.commit()


database = DatabaseOperations()
