from dataclasses import *
import db_types
import misc


TICKET_VIP_PRICE = 23
TICKET_NORMAL_PRICE = 7


class Entity:
    def add_to_table(self):
        q = f"INSERT INTO {self.__class__.__name__} VALUES {astuple(self)};"
        return q

    def __post_init__(self):
        for f in fields(self):
            if issubclass(f.type, db_types.DBType):
                value = getattr(self, f.name)
                setattr(self, f.name, f.type(value))


@dataclass
class Event(Entity):
    Id: db_types.Int = field(init=False, default_factory=misc.IDFactory())
    Name: str
    Date: db_types.Date
    Time: db_types.Time
    Type: str
    Capacity: db_types.Int


@dataclass
class Customer(Entity):
    Id: db_types.Int = field(init=False, default_factory=misc.IDFactory())
    FullName: str
    Email: str
    CreditCard: str


@dataclass
class Ticket(Entity):
    Id: db_types.Int = field(init=False, default_factory=misc.IDFactory())
    Type: str
    Price: float
    IsAvailable: db_types.Bool
    ReservationId: db_types.Int
    EventId: db_types.Int


@dataclass
class Reservation(Entity):
    Id: db_types.Int = field(init=False, default_factory=misc.IDFactory())
    CustomerID: db_types.Int
    EventID: db_types.Int
    NumberOfTickets: db_types.Int
    ReservationDate: db_types.Date
    TotalPrice: float


