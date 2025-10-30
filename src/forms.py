from dataclasses import *
import db_types
import entities


def _get_type(t):
    if t is str:
        return "text"
    elif t is db_types.Int:
        return "number"
    elif t is float:
        return "text"
    elif t is db_types.Date:
        return "date"
    elif t is db_types.Time:
        return "time"
    elif t is db_types.Bool:
        return "checkbox"
    else:
        return str(t.__class__.__name__)

class Form:

    @classmethod
    def to_form(cls):
        return [{"id": f.name, "type":_get_type(f.type)} for f in fields(cls) if f.init]

    @classmethod
    def from_dict(cls, dct):
        return cls(**dict(dct))

    def __post_init__(self):
        self.success_msgs = list()
        self.failure_msgs = list()

        for f in fields(self):
            if issubclass(f.type, db_types.DBType):
                value = getattr(self, f.name)
                setattr(self, f.name, f.type(value))

    def get_success_messages(self):
        return self.success_msgs

    def get_failure_messages(self):
        return self.failure_msgs

    def error(self, msg:str):
        self.failure_msgs.append(msg)

    def success(self, msg:str):
        self.success_msgs.append(msg)

    @classmethod
    def prefetch_data(cls):
        raise NotImplementedError

    def execute(self, db):
        raise NotImplementedError


@dataclass(kw_only=True)
class FormNewCustomer(Form):
    FullName: str
    Email: str
    CreditCard: str

    @classmethod
    def prefetch_data(cls):
        pass

    def execute(self, db):
        customer = entities.Customer(self.FullName, self.Email, self.CreditCard)
        db.execute(customer.add_to_table())
        self.success(f"customer with id: {customer.Id} created")
        return list()


@dataclass(kw_only=True)
class FormNewEvent(Form):
    Name: str
    Date: db_types.Date
    Time: db_types.Time
    Type: str
    NumberOfVIPTickets: db_types.Int
    NumberOfNormalTickets: db_types.Int


    @classmethod
    def prefetch_data(cls):
        pass

    def execute(self, db):
        event = entities.Event(
            self.Name,
            self.Date,
            self.Time,
            self.Type,
            int(self.NumberOfVIPTickets) + int(self.NumberOfNormalTickets)
        )
        db.execute(event.add_to_table())

        for i in range(int(self.NumberOfVIPTickets)):
            t = entities.Ticket("VIP", entities.TICKET_VIP_PRICE, True, None, event.Id)
            db.execute_wait(t.add_to_table())

        for i in range(int(self.NumberOfNormalTickets)):
            t = entities.Ticket("Normal", entities.TICKET_NORMAL_PRICE, True, None, event.Id)
            db.execute_wait(t.add_to_table())

        db.commit()

        self.success(f"event with id: {event.Id} created")
        return list()


@dataclass(kw_only=True)
class FormGetAvailableSeats(Form):
    # TODO: maybe give all the events to the client and see which
    # the client chooses
    EventId: db_types.Int

    @classmethod
    def prefetch_data(cls):
        pass

    def execute(self, db):
        db.execute(f"SELECT Id, Type, Price, IsAvailable FROM Ticket WHERE EventId={self.EventId} AND IsAvailable = TRUE;")
        data = db.fetch()
        if len(data) == 0:
            self.error(f"Event with id {self.EventId} does not exist!")
            return
        return [["Id", "Type", "Price", "IsAvailable"]] + data


@dataclass(kw_only=True)
class FormBookReservation(Form):
    EventId: db_types.Int
    CustomerId: db_types.Int
    NumberOfVIPTickets: db_types.Int
    NumberOfNormalTickets: db_types.Int

    @classmethod
    def prefetch_data(cls):
        pass

    def execute(self, db):
        vip = int(self.NumberOfVIPTickets)
        normal = int(self.NumberOfNormalTickets)

        if vip + normal < 1:
            self.error("Reservation must contain at least 1 ticket")
            return

        db.execute(f"SELECT * FROM Event WHERE Id={self.EventId};")
        event_tup = db.fetch()

        if len(event_tup) == 0:
            self.error("Invalid event id")
            return

        db.execute(f"SELECT * FROM Customer WHERE Id={self.CustomerId};")

        customer_tup = db.fetch()

        if len(customer_tup) == 0:
            self.error("Invalid customer id")
            return

        db.execute(f"SELECT COUNT(*) FROM Ticket WHERE EventId={self.EventId} "
                    "AND IsAvailable=TRUE AND Type='VIP';")
        vip_left = db.fetch(1)[0][0]

        if vip > vip_left:
            self.error(f"Too many vip tickets booked! only {vip_left} left!")
            return

        db.execute(" ".join([
            "SELECT COUNT(*)",
            "FROM Ticket",
            f"WHERE EventId={self.EventId}",
            "AND IsAvailable = TRUE",
            "AND Type='Normal';",
        ]))
        normal_left = db.fetch(1)[0][0]

        if normal > normal_left:
            self.error(f"Too many Normal tickets booked! only {normal_left} left!")
            return

        reservation = entities.Reservation(
            self.CustomerId,
            self.EventId,
            normal + vip,
            db_types.Date.now(),
            entities.TICKET_VIP_PRICE * vip + entities.TICKET_NORMAL_PRICE * normal
        )
        db.execute(reservation.add_to_table())

        db.execute(f"SELECT * FROM Ticket WHERE IsAvailable=TRUE AND Type='Normal' AND EventId={self.EventId}")
        normal_tickets = db.fetch(normal)
        db.execute(f"SELECT * FROM Ticket WHERE IsAvailable=TRUE AND Type='VIP' AND EventId={self.EventId}")
        vip_tickets = db.fetch(vip)

        for ticket in normal_tickets + vip_tickets:
            db.execute_wait("UPDATE Ticket SET"
                            f" ReservationId = {reservation.Id}"
                            ", IsAvailable = FALSE"
                            f" WHERE Id = {ticket[0]}")

        db.commit()

        self.success(f"Reservation with id: {reservation.Id} successfully created")

        return []


@dataclass(kw_only=True)
class FormCancelReservation(Form):
    ReservationId: db_types.Int
    # make tickets with reservation id = reservation id make is available = true
    # delete reservaton entry

    @classmethod
    def prefetch_data(cls):
        pass

    def execute(self, db):
        db.execute(f"SELECT * FROM Reservation WHERE Id={self.ReservationId};")
        results = db.fetch()
        if len(results) == 0:
            self.error(f"invalid reservation Id: {self.ReservationId}")
            return

        db.execute(f"SELECT Id, Type, ReservationId FROM Ticket WHERE ReservationId = {self.ReservationId};")
        tickets_to_be_canceled = db.fetch()

        for t in tickets_to_be_canceled:
            db.execute_wait(f"UPDATE Ticket SET ReservationId = NULL, IsAvailable = TRUE WHERE Id = {t[0]};")

        db.commit()

        db.execute(f"DELETE FROM Reservation WHERE Id = {self.ReservationId};")

        self.success(f"reservation with id {self.ReservationId} has been canceled")

        return [["Id", "Type", "ReservationId"]] + tickets_to_be_canceled


@dataclass(kw_only=True)
class FormCancelEvent(Form):
    EventId: db_types.Int

    @classmethod
    def prefetch_data(cls):
        pass

    def execute(self, db):
        db.execute(f"SELECT * FROM Event WHERE Id={self.EventId};")
        results = db.fetch()
        if len(results) == 0:
            self.error(f"invalid event Id: {self.EventId}")
            return

        db.execute(f"DELETE FROM Ticket WHERE EventId = {self.EventId};")

        db.execute(f"DELETE FROM Reservation WHERE EventId = {self.EventId};")

        db.execute(f"DELETE FROM Event WHERE Id = {self.EventId};")

        self.success(f"Event with id {self.EventId} has been canceled")

        return []


# ----------------- secondary ---------------

@dataclass(kw_only=True)
class FormGetSeatsForEvent(Form):
    EventId: db_types.Int

    @classmethod
    def prefetch_data(cls):
        pass

    def execute(self, db):
        db.execute(f"SELECT * FROM Ticket WHERE EventId={self.EventId};")
        data = db.fetch()
        if len(data) == 0:
            self.error(f"Event with id {self.EventId} does not exist!")
            return

        return [["Id", "Type", "Price", "IsAvailable", "ReservationId", "EventId"]] + data


@dataclass(kw_only=True)
class FormGetIncomeForEvent(Form):
    EventId: db_types.Int

    @classmethod
    def prefetch_data(cls):
        pass

    def execute(self, db):
        db.execute(f"SELECT * FROM Event WHERE Id={self.EventId};")
        event = db.fetch()
        if len(event) == 0:
            self.error(f"Event with id {self.EventId} does not exist!")
            return

        db.execute(f"SELECT SUM(TotalPrice) FROM Reservation WHERE EventId={self.EventId};")
        data = db.fetch()

        event[0] = list(event[0]) + list(data[0])
        return [["Id", "Name", "Date", "Time", "Type", "Capacity", "Income From Event"]] + event


@dataclass(kw_only=True)
class FormGetPopularityByEventReservations(Form):
    @classmethod
    def prefetch_data(cls):
        pass

    def execute(self, db):
        # https://www.w3schools.com/sql/sql_groupby.asp
        db.execute("""
            SELECT EventId, COUNT(Id)
            FROM Reservation
            GROUP BY EventId ORDER BY COUNT(Id) DESC;
        """);
        data = db.fetch()
        if len(data) == 0:
            self.error("No reservations found!")
            return

        return [["Event Id", "Reservations"]] + data

@dataclass(kw_only=True)
class FormGetPopularityByEventIncome(Form):
    DateFrom: db_types.Date
    DateTo: db_types.Date

    @classmethod
    def prefetch_data(cls):
        pass

    def execute(self, db):
        # https://www.w3schools.com/sql/sql_groupby.asp
        db.execute("""
            SELECT EventId, SUM(TotalPrice)
            FROM Reservation
            WHERE {} <= ReservationDate AND ReservationDate <= {}
            GROUP BY EventId ORDER BY SUM(TotalPrice) DESC
        """.format(self.DateFrom, self.DateTo));
        data = db.fetch()

        if len(data) == 0:
            self.error("No reservations found!")
            return

        return [["Event Id", "Income From Event"]] + data


@dataclass(kw_only=True)
class FormGetReservationsPerTimePeriod(Form):
    DateFrom: db_types.Date
    DateTo: db_types.Date

    @classmethod
    def prefetch_data(cls):
        pass

    def execute(self, db):
        db.execute(f"SELECT * FROM Reservation WHERE {self.DateFrom} <= ReservationDate AND ReservationDate <= {self.DateTo};")
        data = db.fetch()
        if len(data) == 0:
            self.error(f"No reservations where made between {self.DateFrom} and {self.DateTo}!")
            return

        return [["Id", "Name", "Date", "Time", "Type", "Capacity"]] + data


@dataclass(kw_only=True)
class FormGetIncome(Form):
    TicketType: str
    ForAllEvents: db_types.Bool = field(default="off")
    EventId: db_types.Int

    @classmethod
    def prefetch_data(cls):
        pass

    def execute(self, db):
        q = "SELECT *, SUM(Price) over () as total_price FROM Ticket WHERE IsAvailable = FALSE"

        if not self.TicketType.lower() in ("vip", "normal", "any", "all"):
            self.error(f"Invalid ticket type: {self.TicketType}")
            return

        if self.TicketType.lower() == "normal":
            q += " AND Type = 'Normal'"
        elif self.TicketType.lower() == "vip":
            q += " AND Type = 'VIP'"

        if not self.ForAllEvents.norm:
            db.execute(f"SELECT Id FROM Event WHERE Id = {self.EventId};")
            data = db.fetch()
            if len(data) == 0:
                self.error(f"Invalid Event Id: {self.EventId}")
                return

            q += f" AND EventId = {self.EventId}"

        q += ";"
        db.execute(q)
        data = db.fetch()
        return [["Ticket Id", "Type", "Price", "IsAvailable", "ReservationId", "EventId", "Total Price"]] + data


Form.forms: dict[str] = {
    "NewCustomer": FormNewCustomer,
    "NewEvent":    FormNewEvent,
    "GetAvailableSeats": FormGetAvailableSeats,
    "BookReservation": FormBookReservation,
    "CancelReservation": FormCancelReservation,
    "CancelEvent": FormCancelEvent,

    # ---- sub questions

    "GetSeatsForEvent": FormGetSeatsForEvent,
    "GetIncomeForEvent": FormGetIncomeForEvent,
    "GetPopularityByEventReservations":FormGetPopularityByEventReservations,
    "GetPopularityByEventIncome":FormGetPopularityByEventIncome,
    "GetReservationsPerTimePeriod":FormGetReservationsPerTimePeriod,
    "GetIncome":FormGetIncome
}
