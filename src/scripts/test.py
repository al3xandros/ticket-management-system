import mysql.connector
from mysql.connector import Error

import settings

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

print("Connected")



