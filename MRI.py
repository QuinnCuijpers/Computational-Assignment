from enum import Enum
from typing import List
from datetime import datetime, timedelta
import heapq


class MRItype(Enum):
    type1 = 1
    type2 = 2


# creates an MRI machine that keeps track of its own time slots
class MRI:
    type: MRItype
    time_slots: List[datetime]  # heapq to implement sorted list
    slot_duration_hours: float

    def __init__(
        self,
        type: MRItype,
        start_date: datetime,
        end_date: datetime,
        slot_duration_hours: float,
    ):
        self.type = type
        self.slot_duration_hours = slot_duration_hours
        self.time_slots = self.generate_time_slots(start_date, end_date)

    def generate_time_slots(
        self, start_date: datetime, end_date: datetime
    ) -> List[datetime]:

        time_slots: List[datetime] = []

        current_time = start_date.replace(hour=8)

        while current_time < end_date:
            while current_time.hour < 17:
                # Add the current slot to the list
                heapq.heappush(time_slots, current_time)

                # Increment the current time by the slot duration
                current_time += timedelta(hours=self.slot_duration_hours)
            current_time = datetime(
                current_time.year, current_time.month, current_time.day, 8, 0, 0
            ) + timedelta(days=1)

        return time_slots

    def get_slot(self, current_date: datetime) -> datetime | None:
        for slot in self.time_slots:
            if slot.date() > current_date.date():
                self.remove_slot(slot)
                return slot
        else:
            return None

    def remove_slot(self, slot: datetime):
        # Book the slot by removing it from available slots
        if slot in self.time_slots:
            self.time_slots.remove(slot)
            heapq.heapify(self.time_slots)  # Re-heapify after removal
        else:
            print("No such timeslot found")


if __name__ == "__main__":
    mri = MRI(MRItype(1), datetime(2023, 12, 1, 0), datetime(2023, 12, 30, 0), 2)

    print(mri.time_slots[0:10])
    slot = mri.get_slot(datetime(2023, 12, 13, 0))
    print(slot)
    slot = mri.get_slot(datetime(2023, 12, 13, 0))
    print(slot)
