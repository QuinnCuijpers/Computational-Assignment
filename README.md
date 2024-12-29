# Computational-Assignment

This project consists of two main parts:
1. Econometrics Part - Statistical analysis of patient data
2. Operations Research Part - A discrete event simulator for MRI scheduling


## Operations Research Part Structure

```mermaid
classDiagram
class Event {
+datetime date
+float scan_duration
+PatientType patient_type
+working_hours_till(Event)
}
class EventCall {
inherits Event
}
class EventScan {
inherits Event
}
class PatientType {
+TYPE_1
+TYPE_2
+from_string(str)
}
class MRItype {
+TYPE_1
+TYPE_2
}
class MRI {
+MRItype type
+Set~datetime~ booked_slots
+float slot_duration_hours
+slot_generator(datetime)
}
class FutureEventsList {
-List~Event~ heap
+add_event(Event)
+pop_event()
+peek_event()
}
class DES {
+datetime date
+List~float~ scan_times
+bool merged
+FutureEventsList future_list
+dict~PatientType,MRI~ MRImachines
+run()
+stats()
}
Event <|-- EventCall
Event <|-- EventScan
Event --> PatientType
MRI --> MRItype
DES --> FutureEventsList
DES --> MRI
FutureEventsList --> Event
```

### Key Components

- **Event System**
  - `Event`: Base class for all events
  - `EventCall`: Represents a patient calling to schedule
  - `EventScan`: Represents the actual scanning appointment

- **MRI Management**
  - `MRI`: Handles individual MRI machine scheduling
  - `MRItype`: Defines different types of MRI machines

- **Scheduling**
  - `FutureEventsList`: Priority queue for event management
  - `DES`: Main discrete event simulator

### Usage

To run the simulation, use the `main()` function in `main.py`.

