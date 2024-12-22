from datetime import datetime, timedelta
from dataclasses import dataclass
from patientType import PatientType


@dataclass
class Event:
    date: datetime
    time: float
    scan_duration: float
    patient_type: PatientType

    def __lt__(self, other: "Event") -> bool:
        self_datetime: datetime = self.date + timedelta(hours=self.time)
        other_datetime: datetime = other.date + timedelta(hours=other.time)
        return self_datetime < other_datetime


class EventCall(Event):

    def __init__(self, date, time, duration, type):
        super().__init__(date, time, duration, type)


class EventScan(Event):

    def __init__(self, date, time, duration, type):
        super().__init__(date, time, duration, type)
