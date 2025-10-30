import database
import settings
from forms import *


db = database.DB()


# Create Customers

for i in range(10):
    FormNewCustomer(
        FullName=f"Customer{i}",
        Email=f"Customer{i}@email.com",
        CreditCard=f"credit-card-{i}"
    ).execute(db)

for i in range(10):
    FormNewEvent(
        Name=f"Event{i}",
        Date=f"20{i:0>2}-02-02",
        Time="22:22",
        Type=f"Type{i}",
        NumberOfVIPTickets=20,
        NumberOfNormalTickets=20
    ).execute(db)

for i in range(10):
    FormBookReservation(
        EventId=i,
        CustomerId=10-i-1,
        NumberOfVIPTickets=3,
        NumberOfNormalTickets=3
    ).execute(db)
    FormBookReservation(
        EventId=i,
        CustomerId=i,
        NumberOfVIPTickets=3,
        NumberOfNormalTickets=3
    ).execute(db)

print("-" * 50)

db.close()

