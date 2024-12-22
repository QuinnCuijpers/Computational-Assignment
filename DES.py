from typing import List
from event import Event, EventCall, EventScan
from utils import read_records
from datetime import datetime, timedelta
from futureEventsList import FutureEventsList
from MRI import MRI, MRItype
from patientType import PatientType


class DES:

    def __init__(
        self,
        filePath,
        start_date: datetime,
        end_date: datetime,
        scan_times: List[float],
    ):
        self.start_date: datetime = start_date
        self.date: datetime = start_date
        self.end_date: datetime = end_date
        self.time = 0.0
        self.future_list: FutureEventsList = read_records(filePath)
        self.scan_times: List[float] = scan_times
        self.waiting_time = 0.0
        self.amount_served = 0
        self.MRImachines: dict[PatientType, MRI] = self.create_MRI(start_date, end_date)

    def create_MRI(self, start_date, end_date) -> dict[PatientType, MRI]:
        d: dict = {}
        for type, scan_time in zip(PatientType, self.scan_times):
            d[type] = MRI(MRItype(type.value), start_date, end_date, scan_time)
        return d

    # create scan appointment
    def handle_call(self, event: EventCall):
        if event.date.date() > datetime(2023, 8, 30).date():
            return
        # create a scanning time
        mri: MRI = self.MRImachines[event.patient_type]
        slot: datetime | None = mri.get_slot(event.date)
        if slot:
            time: float = slot.hour + slot.minute / 60
            new_event = EventScan(slot, time, event.scan_duration, event.patient_type)
            self.future_list.add_event(new_event)
            # gives the full waiting time, but we need the waiting time in operational hours
            # waiting_time: timedelta = new_event.date - event.date
            # waiting_time_hours: float = waiting_time.total_seconds() / 3600
            # self.waiting_time += waiting_time_hours
        # else:
        #     print(f"No timeslot available for the call on {event.date} at {event.time}")

    # take up mri for scan_duration?
    def handle_scan(self, event: EventScan):
        if (
            event.scan_duration
            > self.MRImachines[event.patient_type].slot_duration_hours
        ):
            print("time limit exeeded")
        self.amount_served += 1

    # main loop
    def run(self) -> None:
        while self.future_list:
            event: Event = self.future_list.pop_event()
            self.time = event.time
            self.date = event.date
            match event:
                case EventCall():
                    self.handle_call(event)
                case EventScan():
                    self.handle_scan(event)
                case _:
                    raise ValueError("Unhandled event")

    def stats(self):
        print(f"Amount of patients that finished their MRI: {self.amount_served}")
