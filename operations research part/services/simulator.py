from typing import Any, Generator, List, NoReturn, Dict
from pathlib import Path
from models.event import Event, EventCall, EventScan
from utils.file_reader import read_records
from datetime import datetime, date
from services.event_list import FutureEventsList
from models.mri import MRI, MRItype
from models.patient import PatientType


class DES:

    current_date: datetime
    scan_times: List[float]
    merged: bool
    future_list: FutureEventsList
    MRImachines: dict[PatientType, MRI]
    total_waiting_time: float
    amount_served: int
    max_waiting_time: float
    total_overtime: float
    total_delay: float
    max_delay: float
    delays_by_date: Dict[date, List[float]]

    def __init__(self, filePath: Path, scan_times: List[float], merged: bool) -> None:
        if len(scan_times) != len(PatientType):
            raise ValueError("Number of scan times must match number of patient types")

        self.scan_times = scan_times
        self.merged = merged
        self.future_list = read_records(filePath)
        self.MRImachines = self.create_MRI_machines()

        # Initialize statistics
        self.total_waiting_time = 0.0
        self.amount_served = 0
        self.max_waiting_time = 0.0
        self.total_overtime = 0.0

        # delay statistics
        self.total_delay = 0.0
        self.max_delay = 0.0
        self.delays_by_date: Dict[date, List[float]] = {}

    def create_MRI_machines(self) -> dict[PatientType, MRI]:
        d: dict = {}
        for type, scan_time in zip(PatientType, self.scan_times):
            d[type] = MRI(MRItype(type.value), scan_time)
        return d

    # create scan appointment
    def handle_call(self, event: EventCall) -> None:
        if self.merged:
            slot, selected_mri = self._find_best_slot(event)
            selected_mri.booked_slots.add(slot)
        else:
            mri = self.MRImachines[event.patient_type]
            slot = next(mri.slot_generator(event.date))
            mri.booked_slots.add(slot)

        # Calculate waiting time and update statistics
        waiting_time = event.working_hours_till(
            Event(slot, event.scan_duration, event.patient_type)
        )
        self.total_waiting_time += waiting_time
        self.max_waiting_time = max(self.max_waiting_time, waiting_time)

        # Create and schedule the scan event
        scan_event = EventScan(slot, event.scan_duration, event.patient_type)
        self.future_list.add_event(scan_event)

    def _find_best_slot(self, event: EventCall) -> tuple[datetime, MRI]:
        best_slot = datetime.max
        best_mri: MRI = next(
            iter(self.MRImachines.values())
        )  # Initialize with first MRI
        for mri in self.MRImachines.values():
            slot = next(mri.slot_generator(event.date))
            if slot < best_slot:
                best_slot = slot
                best_mri = mri
        return best_slot, best_mri

    def handle_scan(self, event: EventScan) -> None:
        self.amount_served += 1

        # Get actual scan duration from scan_times list
        actual_duration = event.scan_duration

        # Get MRI machine and calculate delay
        mri = self.MRImachines[event.patient_type]
        delay = mri.add_delay(event.date, actual_duration)

        # Update delay statistics
        self.total_delay += delay
        self.max_delay = max(self.max_delay, delay)

        # Track delays by date
        event_date = event.date.date()
        if event_date not in self.delays_by_date:
            self.delays_by_date[event_date] = []
        self.delays_by_date[event_date].append(delay)

        # Calculate end time including delay
        end_time = event.date.hour + event.date.minute / 60 + actual_duration

        # Calculate overtime
        overtime = max(0, end_time - 17)
        self.total_overtime += overtime

    # main loop
    def run(self) -> None:
        while self.future_list:
            event: Event = self.future_list.pop_event()
            self.current_date = event.date
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
            f"last day that a scan was scheduled: {self.current_date.date()} at {self.current_date.time()}"
        )
        print(f"Maximum waiting time in operational hours: {self.max_waiting_time}")
        print(f"Total overtime used: {self.total_overtime}")

        # New delay statistics
        print(f"\nDelay Statistics:")
        print(
            f"Average delay per customer: {self.total_delay/self.amount_served:.2f} hours"
        )
        print(f"Maximum delay: {self.max_delay:.2f} hours")

        # Calculate average delay per day
        daily_averages = {
            date: sum(delays) / len(delays)
            for date, delays in self.delays_by_date.items()
        }
        if daily_averages:
            avg_daily_delay = sum(daily_averages.values()) / len(daily_averages)
            print(f"Average delay per day: {avg_daily_delay:.2f} hours")
