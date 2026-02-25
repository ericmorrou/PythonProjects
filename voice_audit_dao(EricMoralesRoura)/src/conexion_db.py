import psycopg2
from src.config import Config

class ConexionDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConexionDB, cls).__new__(cls)
            cls._instance._connection = None
        return cls._instance

    def get_connection(self):
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(
                    host=Config.DB_HOST,
                    database=Config.DB_NAME,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    port=Config.DB_PORT
                )
                print("Conexión a base de datos establecida.")
            except psycopg2.Error as e:
                print(f"Error al conectar a la base de datos: {e}")
                raise
        return self._connection

    def close_connection(self):
        if self._connection and not self._connection.closed:
            self._connection.close()
            print("Conexión cerrada.")
