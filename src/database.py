import mysql.connector
import settings

class DB:
    def __init__(self):
        self.succeeded = False
        try:
            connection = mysql.connector.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_DATABASE,
                connection_timeout=settings.DB_TIMEOUT
            )
        except Exception as e:
            print("Could not connect to database.")
            exit(1)

        self.succeeded = True
        self.connection = connection 
        self.cursor = self.connection.cursor(buffered=True)

    def execute_batch(self, *queries:list[str]):
        for query in queries:
            print(query)
            self.cursor.execute(query)
        self.connection.commit()

    def execute(self, *args, **kwargs):
        self.execute_wait(*args, **kwargs)
        self.connection.commit()

    def close(self):
        if not self.succeeded:
            return

        if not self.connection.is_connected():
            return

        self.connection.commit()
        self.connection.close()
        self.close()

    def execute_wait(self, *args, **kwargs):
        print(args)
        self.cursor.execute(*args, **kwargs)

    def commit(self):
        self.connection.commit()

    def fetch(self, n: int = None):
        if n is None:
            r = self.cursor.fetchall()
        elif n <= 0:
            self.cursor.fetchall()
            r = list()
        elif n == 1:
            r = self.cursor.fetchone()
        else:
            r = self.cursor.fetchmany(n)

        if isinstance(r, tuple):
            return [r]

        return r

    def __del__(self):
        self.close()
