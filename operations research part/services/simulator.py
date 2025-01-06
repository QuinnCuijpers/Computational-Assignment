from typing import Any, Generator, List, NoReturn, Dict, DefaultDict
from pathlib import Path
from models.event import Event, EventCall, EventScan
from utils.file_reader import read_records
from datetime import datetime, date, timedelta
from services.event_list import FutureEventsList
from models.mri import MRI, MRItype
from models.patient import PatientType
from collections import defaultdict


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
    delays_by_date: DefaultDict[date, List[float]]
    last_scheduled_date: datetime
    max_overtime: float

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
        self.max_overtime = 0.0

        # delay statistics
        self.total_delay = 0.0
        self.delays_by_date: DefaultDict[date, List[float]] = defaultdict(list)

        self.last_scheduled_date: datetime = datetime.min
        self.current_date: datetime = datetime.min

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
            slot = next(mri.slot_generator(event.start_date))
            mri.booked_slots.add(slot)

        # Update last scheduled date when creating a new scan
        self.last_scheduled_date = max(self.last_scheduled_date, slot)

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
            slot = next(mri.slot_generator(event.start_date))
            if slot < best_slot:
                best_slot = slot
                best_mri = mri
        return best_slot, best_mri

    def handle_scan(self, event: EventScan) -> None:
        self.amount_served += 1

        # Get MRI machine and calculate delays
        mri = self.MRImachines[event.patient_type]
        current_delay = max(
            0, event.scan_duration - mri.slot_duration_hours
        )  # New delay from this scan
        accumulated_delay = mri.get_accumulated_delay(
            event.start_date
        )  # Previous delays
        total_delay = current_delay + accumulated_delay

        # Store the total delay for this time slot
        mri.store_delay(event.start_date, total_delay)

        # Add total delay to event for end time calculation
        event.add_delay(current_delay)

        # Add scan time to MRI utilization tracking
        mri.add_scan_time(event.scan_duration)

        # Update delay statistics
        self.total_delay += current_delay

        # Track delays by date
        self.delays_by_date[event.start_date.date()].append(current_delay)

        # Update current simulation time to end of scan
        self.current_date = event.end_date

        # Calculate and update overtime statistics
        overtime = event.calculate_overtime()
        self.total_overtime += overtime
        self.max_overtime = max(self.max_overtime, overtime)

    # main loop
    def run(self) -> None:
        while self.future_list:
            event: Event = self.future_list.pop_event()
            self.current_date = event.start_date
            match event:
                case EventCall():
                    self.handle_call(event)
                case EventScan():
                    self.handle_scan(event)
                case _:
                    raise ValueError("Unhandled event")

    def stats(self) -> None:

        # waiting time statistics
        print(f"\nWaiting time statistics:")
        print(
            f"Average waiting time in operational hours: {self.total_waiting_time/self.amount_served}"
        )
        print(f"Maximum waiting time in operational hours: {self.max_waiting_time}")

        # last scan day
        print(f"\nLast scan day:")
        print(
            f"Last day that a scan was scheduled: {self.last_scheduled_date.date()} at {self.last_scheduled_date.time()}"
        )
        print(
            f"Last day that a scan finished: {self.current_date.date()} at {self.current_date.time()}"
        )

        # Overtime statistics
        print(f"\nOvertime Statistics:")
        print(f"Total overtime used: {self.total_overtime:.2f} hours")
        print(f"Maximum overtime in a day: {self.max_overtime:.2f} hours")

        # Delay statistics
        print(f"\nDelay Statistics:")
        print(
            f"Average delay per customer: {self.total_delay/self.amount_served:.2f} hours"
        )

        # Calculate average delay per day (modified)
        total_days = len(self.delays_by_date)
        if total_days > 0:
            total_daily_delay = sum(
                sum(delays) for delays in self.delays_by_date.values()
            )
            avg_daily_delay = total_daily_delay / total_days
            print(f"Average total delay per day: {avg_daily_delay:.2f} hours")

            # Also show average delay per scan for context
            print(
                f"Average delay per scan: {self.total_delay/self.amount_served:.2f} hours"
            )

        print(f"\nMRI Utilization:")
        first_event = min(self.delays_by_date.keys())
        for patient_type, mri in self.MRImachines.items():
            utilization = mri.calculate_utilization(
                self.current_date, datetime.combine(first_event, datetime.min.time())
            )
            print(f"MRI {patient_type.name}: {utilization:.1f}%")
