from enum import Enum, auto
import numpy as np
from typing import Generator, NoReturn, Set, Any
from datetime import datetime, timedelta


class MRItype(Enum):
    # Enumeration for different types of MRI machines
    # Corresponds to patient types they can serve when merged is false
    TYPE_1 = auto()
    TYPE_2 = auto()


# creates an MRI machine that keeps track of its own time slots
class MRI:
    # Represents an MRI machine with its scheduling capabilities
    type: MRItype
    booked_slots: Set[datetime]  # Keeps track of all booked time slots
    slot_duration_hours: float  # Duration of each scanning slot

    def __init__(
        self,
        type: MRItype,
        slot_duration_hours: float,
    ) -> None:
        # Initialize an MRI machine with its type and slot duration
        self.type = type
        self.slot_duration_hours = slot_duration_hours
        self.booked_slots: Set[datetime] = set()

    def slot_generator(
        self, current_date: datetime
    ) -> Generator[datetime, Any, NoReturn]:
        # Generates available time slots for scheduling
        # Starts from the next day and continues indefinitely
        # Only generates slots during working hours (8:00-17:00)

        # Reset to start of next day
        search_date = current_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)

        while True:
            # Generate slots for each working hour of a day
            for hour in np.arange(8, 17, self.slot_duration_hours):
                potential_slot = search_date + timedelta(hours=float(hour))
                # Only yield slots that are within working hours and not already booked
                if potential_slot.hour < 17 and potential_slot not in self.booked_slots:
                    yield potential_slot
            search_date += timedelta(days=1)
