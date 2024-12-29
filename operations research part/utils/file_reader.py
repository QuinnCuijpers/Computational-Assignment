from datetime import datetime, timedelta
from models.patient import PatientType
from services.event_list import FutureEventsList
from models.event import EventCall
from pathlib import Path


def read_records(path: Path) -> FutureEventsList:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    event_list = FutureEventsList()
    with path.open("r") as f:
        lines = f.readlines()

        if not lines:
            raise ValueError("Empty file")

        for line in lines[1:]:  # Skip header
            date, time, duration, patient_type_str = line.strip().split(",")
            patient_time = float(time)
            patient_date = datetime.strptime(date, "%Y-%m-%d") + timedelta(
                hours=patient_time
            )
            patient_duration = float(duration)
            patient_type = PatientType.from_string(patient_type_str.strip('""'))

            event = EventCall(patient_date, patient_duration, patient_type)
            event_list.add_event(event)
    return event_list
