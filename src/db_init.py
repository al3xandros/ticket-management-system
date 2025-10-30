import mysql.connector
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
    print(e)
    exit(1)

cursor = connection.cursor()

cursor.execute(f"DROP DATABASE IF EXISTS {settings.DB_DATABASE};")
cursor.execute(f"CREATE DATABASE {settings.DB_DATABASE};")
cursor.execute(f"USE {settings.DB_DATABASE};")

connection.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS Event (
    Id INT PRIMARY KEY NOT NULL,
    Name VARCHAR(1000),
    Date DATE,
    Time TIME,
    Type VARCHAR(1000),
    Capacity INT
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS Customer (
    Id INT PRIMARY KEY NOT NULL,
    FullName VARCHAR(1000),
    Email VARCHAR(1000),
    CreditCard VARCHAR(1000)
);""")


cursor.execute("""CREATE TABLE IF NOT EXISTS Reservation (
    Id INT PRIMARY KEY NOT NULL,
    CustomerId INT,
    EventId INT,
    NumberOfTickets INT,
    ReservationDate DATE,
    TotalPrice DOUBLE,
    FOREIGN KEY (CustomerId) REFERENCES Customer(Id),
    FOREIGN KEY (EventId) REFERENCES Event(Id)
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS Ticket (
    Id INT PRIMARY KEY NOT NULL,
    Type VARCHAR(1000),
    Price DOUBLE,
    IsAvailable BOOLEAN,
    ReservationId INT,
    EventId INT,

    FOREIGN KEY (EventId) REFERENCES Event(Id),
    FOREIGN KEY (ReservationId) REFERENCES Reservation(Id)
);""")

cursor.close()
connection.close()

