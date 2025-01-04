from enum import Enum, auto
import numpy as np
from typing import Generator, NoReturn, Set, Any, Dict
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
    delays: Dict[datetime, float]  # Maps slot start times to delay durations

    def __init__(
        self,
        type: MRItype,
        slot_duration_hours: float,
    ) -> None:
        # Initialize an MRI machine with its type and slot duration
        self.type = type
        self.slot_duration_hours = slot_duration_hours
        self.booked_slots: Set[datetime] = set()
        self.delays: Dict[datetime, float] = {}

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
                # Account for accumulated delays
                delay = self.get_accumulated_delay(potential_slot)
                adjusted_slot = potential_slot + timedelta(hours=delay)

                # Only yield slots that are within working hours and not already booked
                if adjusted_slot.hour < 17 and potential_slot not in self.booked_slots:
                    yield potential_slot
            search_date += timedelta(days=1)

    def calculate_total_delay(self, slot: datetime, actual_duration: float) -> float:
        # Calculate total delay including both current scan's delay and accumulated delays
        current_delay = max(0, actual_duration - self.slot_duration_hours)
        accumulated_delay = self.get_accumulated_delay(slot)
        return current_delay + accumulated_delay

    def store_delay(self, slot: datetime, delay: float) -> None:
        # Store delay if it's greater than zero
        if delay > 0:
            self.delays[slot] = delay

    def get_accumulated_delay(self, slot: datetime) -> float:
        # Calculate accumulated delays affecting this slot
        total_delay = 0.0
        for delay_slot, delay_duration in self.delays.items():
            if delay_slot < slot and delay_slot.date() == slot.date():
                total_delay += delay_duration
        return total_delay
