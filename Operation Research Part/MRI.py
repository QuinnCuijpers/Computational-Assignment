from enum import Enum
import numpy as np
from typing import Generator, NoReturn, Set, Any
from datetime import datetime, timedelta


class MRItype(Enum):
    TYPE_1 = 1
    TYPE_2 = 2


# creates an MRI machine that keeps track of its own time slots
class MRI:
    type: MRItype
    booked_slots: Set[datetime]  # set of booked slots
    slot_duration_hours: float

    def __init__(
        self,
        type: MRItype,
        slot_duration_hours: float,
    ):
        self.type = type
        self.slot_duration_hours = slot_duration_hours
        self.booked_slots = set()

    def slot_generator(
        self, current_date: datetime
    ) -> Generator[datetime, Any, NoReturn]:

        current_date = current_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )  # Normalize to the first operating hour of the day
        search_date: datetime = current_date + timedelta(
            days=1
        )  # Start with the next day

        while True:
            search_date.replace(hour=0, minute=0, second=0)
            for hour in np.arange(8, 17, self.slot_duration_hours):
                potential_slot: datetime = search_date + timedelta(hours=float(hour))
                # skip time slots starting after 5 pm
                if potential_slot.hour >= 17:
                    if potential_slot.minute > 0:
                        continue
                elif potential_slot not in self.booked_slots:
                    yield potential_slot

            # Move to the next day
            search_date += timedelta(days=1)
