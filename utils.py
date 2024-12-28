from datetime import datetime, timedelta
from patientType import PatientType
from futureEventsList import FutureEventsList
from event import EventCall


def read_records(path) -> FutureEventsList:

    eventList = FutureEventsList()
    with open(path, "r") as f:

        lines: list[str] = f.readlines()
        stripped_lines: list[str] = [line.strip() for line in lines]
        for i, line in enumerate(stripped_lines):
            # discard column names so start with 1
            if i == 0:
                continue
            date, time, duration, patientType = line.split(",")
            patient_time = float(time)
            patient_date: datetime = datetime.strptime(date, "%Y-%m-%d") + timedelta(
                hours=patient_time
            )
            patient_duration = float(duration)
            patient_type: PatientType = PatientType.from_string(patientType.strip('""'))

            event = EventCall(patient_date, patient_duration, patient_type)
            eventList.add_event(event)
    return eventList
