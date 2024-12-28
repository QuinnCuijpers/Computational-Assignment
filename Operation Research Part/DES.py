from typing import Any, Generator, List, NoReturn
from pathlib import Path
from event import Event, EventCall, EventScan
from utils import read_records
from datetime import datetime
from futureEventsList import FutureEventsList
from MRI import MRI, MRItype
from patientType import PatientType


class DES:

    date: datetime
    scan_times: List[float]
    merged: bool
    future_list: FutureEventsList
    MRImachines: dict[PatientType, MRI]
    total_waiting_time: float
    amount_served: int
    max_waiting_time: float
    total_overtime: float

    def __init__(self, filePath: Path, scan_times: List[float], merged: bool):
        self.scan_times = scan_times
        self.merged = merged

        self.future_list = read_records(filePath)
        self.MRImachines = self.create_MRI_machines()

        self.total_waiting_time = 0.0
        self.amount_served = 0
        self.max_waiting_time = 0.0
        self.total_overtime = 0.0

    def create_MRI_machines(self) -> dict[PatientType, MRI]:
        d: dict = {}
        for type, scan_time in zip(PatientType, self.scan_times):
            d[type] = MRI(MRItype(type.value), scan_time)
        return d

    # create scan appointment
    def handle_call(self, event: EventCall):
        # create a scanning time
        if not self.merged:
            mri: MRI = self.MRImachines[event.patient_type]
            gen: Generator[datetime, Any, NoReturn] = mri.slot_generator(event.date)
            slot: datetime = next(gen)
            mri.booked_slots.add(slot)
        else:
            best_slot: datetime = datetime.max
            for mri in self.MRImachines.values():
                gen = mri.slot_generator(event.date)
                slot = next(gen)
                if slot < best_slot:
                    best_slot = slot
                    best_mri = mri
            slot = best_slot
            best_mri.booked_slots.add(slot)
        if slot:
            if (
                event.scan_duration
                > self.MRImachines[event.patient_type].slot_duration_hours
            ):
                raise ValueError(
                    f"Time slot not sufficient for all scan durations, namely: scan from {event.patient_type} at {event.date} with duration = {event.scan_duration}"
                )
            new_event = EventScan(slot, event.scan_duration, event.patient_type)
            self.future_list.add_event(new_event)

            # waiting time calculation:
            time_diff: float = event.working_hours_till(new_event)
            self.total_waiting_time += time_diff
            self.max_waiting_time = max(time_diff, self.max_waiting_time)

    # take up mri for scan_duration?
    def handle_scan(self, event: EventScan):
        self.amount_served += 1
        overtime: float = (
            event.date.hour + self.scan_times[event.patient_type.value - 1] - 17
        )
        if overtime > 0:
            self.total_overtime += overtime

    # main loop
    def run(self) -> None:
        while self.future_list:
            event: Event = self.future_list.pop_event()
            self.date = event.date
            match event:
                case EventCall():
                    self.handle_call(event)
                case EventScan():
                    self.handle_scan(event)
                case _:
                    raise ValueError("Unhandled event")

    def stats(self) -> None:
        print(
            f"Average waiting time in operational hours: {self.total_waiting_time/self.amount_served}"
        )
        print(
            f"last day that a scan was scheduled: {self.date.date()} at {self.date.time()}"
        )
        print(f"Maximum waiting time in operational hours: {self.max_waiting_time}")
        print(f"Total overtime used: {self.total_overtime}")
