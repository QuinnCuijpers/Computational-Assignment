from datetime import datetime, timedelta
from dataclasses import dataclass
from patientType import PatientType


@dataclass
class Event:
    date: datetime
    scan_duration: float
    patient_type: PatientType

    def __lt__(self, other: "Event") -> bool:
        return self.date < other.date

    def working_hours_till(self, event: "Event") -> float:

        total_hours = 0.0
        current_date: datetime = self.date

        while current_date < event.date:
            # Calculate the next hour increment or end time of the period
            next_hour: datetime = min(current_date + timedelta(hours=1), event.date)

            # Check if the current hour is within the operating window
            if 8 <= current_date.hour < 17:
                # Add the fractional hour within this range
                hour_diff = (next_hour - current_date).total_seconds() / 3600
                total_hours += hour_diff

            # Move to the next hour increment
            current_date = next_hour

        return total_hours


class EventCall(Event):

    def __init__(self, date, duration, type):
        super().__init__(date, duration, type)


class EventScan(Event):

    def __init__(self, date, duration, type):
        super().__init__(date, duration, type)
