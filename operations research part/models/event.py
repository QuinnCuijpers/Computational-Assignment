from datetime import datetime, timedelta
from dataclasses import dataclass
from models.patient import PatientType


@dataclass
class Event:
    # Base class for all events in the simulation
    # date: when the event occurs
    # scan_duration: how long the scan takes
    # patient_type: Type 1 or Type 2 patient
    date: datetime
    scan_duration: float
    patient_type: PatientType

    def __lt__(self, other: "Event") -> bool:
        # Comparison method for event ordering
        # Allows events to be sorted chronologically in the priority queue
        return self.date < other.date

    def working_hours_till(self, event: "Event") -> float:
        # Calculates the number of working hours between this event and another event
        # Only counts hours between 8:00 and 17:00 (working hours)
        if self.date >= event.date:
            raise ValueError("Event date is before current date")

        total_hours = 0.0
        current_date = self.date

        # Iterate through time in 1-hour increments until we reach the target event
        while current_date < event.date:
            # Calculate the next hour, but don't go past the target event
            next_hour = min(current_date + timedelta(hours=1), event.date)
            # Only count hours during working time (8:00-17:00)
            if 8 <= current_date.hour < 17:
                total_hours += (next_hour - current_date).total_seconds() / 3600
            current_date = next_hour

        return total_hours


@dataclass
class EventCall(Event):
    # Represents a patient calling to schedule an appointment
    # Inherits all attributes from Event
    pass


@dataclass
class EventScan(Event):
    # Represents the actual scanning appointment
    # Inherits all attributes from Event
    pass
