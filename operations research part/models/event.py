from datetime import datetime, timedelta
from dataclasses import dataclass
from models.patient import PatientType


@dataclass
class Event:
    date: datetime
    scan_duration: float
    patient_type: PatientType

    def __lt__(self, other: "Event") -> bool:
        return self.date < other.date

    def working_hours_till(self, event: "Event") -> float:
        if self.date >= event.date:
            raise ValueError("Event date is before current date")

        total_hours = 0.0
        current_date = self.date

        while current_date < event.date:
            next_hour = min(current_date + timedelta(hours=1), event.date)
            if 8 <= current_date.hour < 17:
                total_hours += (next_hour - current_date).total_seconds() / 3600
            current_date = next_hour

        return total_hours


@dataclass
class EventCall(Event):
    pass


@dataclass
class EventScan(Event):
    pass
