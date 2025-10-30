import re
import datetime

class DBType:
    def __str__(self):
        return self.__repr__()


class Time(DBType):
    def __init__(self, val):
        if type(val) is Time:
            self.val = val.val

        elif not re.match(r"^\d\d:\d\d$", val):
            self.val = val + ":00"

        elif not re.match(r"^\d\d:\d\d:\d\d$", val):
            self.val = val

        elif val is None:
            self.val = "NULL"

        else:
            raise Exception(f"Could not parse as {self.__class__.__name__}")

    def __repr__(self):
        return f"'{self.val}'"

    @classmethod
    def now(cls):
        x = datetime.datetime.now()
        return cls(x.strftime(r"%H:%M:00"))


class Date(DBType):
    def __init__(self, val):
        if type(val) is Date:
            self.val = val.val

        elif re.match(r"^\d\d\d\d-[0-1]\d-[0-3]\d$", val):
            self.val = val

        elif val is None:
            self.val = "NULL"

        else:
            raise Exception(f"Could not parse as {self.__class__.__name__}")

    def __repr__(self):
        return f"'{self.val}'"

    @classmethod
    def now(cls):
        x = datetime.datetime.now()
        return cls(x.strftime(r"%Y-%m-%d"))


class Bool(DBType):
    def __init__(self, val):
        if type(val) is Bool:
            self.val = val.val

        elif type(val) is bool:
            self.val = str(val).upper()

        elif str(val).upper() in ("ON", "OFF"):
            self.val = "TRUE" if str(val).upper() == "ON" else "FALSE"

        elif str(val).upper() in ("TRUE", "FALSE"):
            self.val = val

        elif val is None:
            self.val = "NULL"

        else:
            raise Exception(f"Could not parse as {self.__class__.__name__}")

        if self.val == "NULL":
            self.norm = None
        else:
            self.norm = self.val == "TRUE"

    def __repr__(self):
        return f"{str(self.val).upper()}"

    def __bool__(self):
        return self.norm

class Int(DBType):
    def __init__(self, val):
        if type(val) is Int:
            self.val = val.val

        elif type(val) is int:
            self.val = str(val)

        elif re.match(r"^[0-9]+$", str(val)):
            self.val = str(val)

        elif val is None:
            self.val = "NULL"

        else:
            raise Exception(f"Could not parse as {self.__class__.__name__}")

        if self.val == "NULL":
            self.norm = None
        else:
            self.norm = int(self.val)

    def __int__(self):
        return self.norm

    def __repr__(self):
        return f"{str(self.val)}"
