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
    total_scan_time: float  # Track total time machine is used

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
        self.total_scan_time: float = 0.0  # Track total time machine is used

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

                potential_slot_end = potential_slot + timedelta(
                    hours=self.slot_duration_hours
                )

                if potential_slot_end.hour > 17 or (
                    potential_slot_end.hour == 17 and potential_slot_end.minute > 0
                ):
                    continue

                # Don't adjust the slot time with delays when checking availability
                if potential_slot not in self.booked_slots:
                    yield potential_slot
            search_date += timedelta(days=1)

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

    def add_scan_time(self, duration: float) -> None:
        self.total_scan_time += duration

    def calculate_utilization(self, end_date: datetime, start_date: datetime) -> float:
        # Calculate total working hours between start and end date
        total_days = (end_date.date() - start_date.date()).days + 1
        working_hours_per_day = 9  # 8:00 to 17:00
        total_working_hours = total_days * working_hours_per_day

        # Return utilization percentage
        return (
            (self.total_scan_time / total_working_hours) * 100
            if total_working_hours > 0
            else 0
        )
