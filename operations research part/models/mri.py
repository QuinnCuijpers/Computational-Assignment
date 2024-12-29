from enum import Enum, auto
import numpy as np
from typing import Generator, NoReturn, Set, Any
from datetime import datetime, timedelta


class MRItype(Enum):
    TYPE_1 = auto()
    TYPE_2 = auto()


# creates an MRI machine that keeps track of its own time slots
class MRI:
    type: MRItype
    booked_slots: Set[datetime]  # set of booked slots
    slot_duration_hours: float

    def __init__(
        self,
        type: MRItype,
        slot_duration_hours: float,
    ) -> None:
        self.type = type
        self.slot_duration_hours = slot_duration_hours
        self.booked_slots: Set[datetime] = set()

    def slot_generator(
        self, current_date: datetime
    ) -> Generator[datetime, Any, NoReturn]:
        search_date = current_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)

        while True:
            for hour in np.arange(8, 17, self.slot_duration_hours):
                potential_slot = search_date + timedelta(hours=float(hour))
                if potential_slot.hour < 17 and potential_slot not in self.booked_slots:
                    yield potential_slot
            search_date += timedelta(days=1)
