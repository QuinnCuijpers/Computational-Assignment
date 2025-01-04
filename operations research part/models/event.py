from datetime import datetime, timedelta
from dataclasses import dataclass, field
from models.patient import PatientType


@dataclass
class Event:
    # Base class for all events in the simulation
    # date: when the event occurs
    # scan_duration: how long the scan takes
    # patient_type: Type 1 or Type 2 patient
    start_date: datetime
    scan_duration: float
    patient_type: PatientType

    def __lt__(self, other: "Event") -> bool:
        # Comparison method for event ordering
        # Allows events to be sorted chronologically in the priority queue
        return self.start_date < other.start_date

    def working_hours_till(self, event: "Event") -> float:
        # Calculates the number of working hours between this event and another event
        # Only counts hours between 8:00 and 17:00 (working hours)
        if self.start_date >= event.start_date:
            raise ValueError("Event date is before current date")

        total_hours = 0.0
        current_date = self.start_date

        # Iterate through time in 1-hour increments until we reach the target event
        while current_date < event.start_date:
            # Calculate the next hour, but don't go past the target event
            next_hour = min(current_date + timedelta(hours=1), event.start_date)
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
    end_date: datetime = field(init=False)
    _delay: float = field(default=0.0, init=False)

    def __post_init__(self):
        # Calculate initial end time based on scan duration
        self._update_end_date()

    def _update_end_date(self) -> None:
        # Calculate end time including both scan duration and any delays
        total_hours = self.scan_duration + self._delay
        self.end_date = self.start_date + timedelta(hours=total_hours)

    def add_delay(self, delay: float) -> None:
        # Add delay and update end time
        self._delay += delay
        self._update_end_date()

    def calculate_overtime(self) -> float:
        # Calculate overtime (time past 17:00)
        end_time = self.end_date.hour + self.end_date.minute / 60
        return max(0, end_time - 17)
