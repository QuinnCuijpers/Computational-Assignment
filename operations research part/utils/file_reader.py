from datetime import datetime, timedelta
from models.patient import PatientType
from services.event_list import FutureEventsList
from models.event import EventCall
from pathlib import Path


def read_records(path: Path) -> FutureEventsList:
    # Reads and parses patient records from a CSV file
    # Returns a FutureEventsList containing EventCall objects for each patient

    # Verify file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    event_list = FutureEventsList()
    with path.open("r") as f:
        lines = f.readlines()

        if not lines:
            raise ValueError("Empty file")

        # Process each line (skipping header)
        for line in lines[1:]:
            # Parse CSV format: date,time,duration,patient_type
            date, time, duration, patient_type_str = line.strip().split(",")

            # Convert time to float and create full datetime
            patient_time = float(time)
            patient_date = datetime.strptime(date, "%Y-%m-%d") + timedelta(
                hours=patient_time
            )

            # Parse duration and patient type
            patient_duration = float(duration)
            patient_type = PatientType.from_string(patient_type_str.strip('""'))

            # Create and add event to the list
            event = EventCall(patient_date, patient_duration, patient_type)
            event_list.add_event(event)
    return event_list
