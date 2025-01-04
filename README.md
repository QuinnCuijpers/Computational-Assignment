# Computational-Assignment

This project consists of two main parts:
1. Econometrics Part - Statistical analysis of patient data
2. Operations Research Part - A discrete event simulator for MRI scheduling


## Operations Research Part Structure

```mermaid
classDiagram
class Event {
+datetime start_date
+float scan_duration
+PatientType patient_type
+working_hours_till(Event)
+__lt__(Event)
}
class EventCall {
inherits Event
}
class EventScan {
inherits Event
+datetime end_date
+add_delay(float)
+calculate_overtime()
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
+Set[datetime] booked_slots
+Dict[datetime,float] delays
+float slot_duration_hours
+slot_generator(datetime)
+calculate_total_delay(datetime, float)
+store_delay(datetime, float)
+get_accumulated_delay(datetime)
}
class FutureEventsList {
-List[Event] heap
+add_event(Event)
+pop_event()
+peek_event()
}
class DES {
+datetime current_date
+datetime last_scheduled_date
+List[float] scan_times
+bool merged
+FutureEventsList future_list
+Dict[PatientType,MRI] MRImachines
+DefaultDict[date, List[float]] delays_by_date
+run()
+stats()
+handle_scan(EventScan)
+handle_call(EventCall)
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

#### Models
- **Event** (`models/event.py`): Base class for simulation events
  - `EventCall`: Patient appointment request events
  - `EventScan`: MRI scanning events with end time tracking and delay management
  - Handles working hours calculations and event ordering

- **MRI** (`models/mri.py`): MRI machine management
  - `MRItype`: Enum for machine types
  - Handles slot scheduling and availability
  - Manages delays and their accumulation throughout the day

- **PatientType** (`models/patient.py`): Patient classification
  - Enum for different patient types
  - Handles conversion from string representations

#### Services
- **FutureEventsList** (`services/event_list.py`): Event queue management
  - Priority queue implementation for events
  - Maintains chronological event ordering

- **DES** (`services/simulator.py`): Discrete Event Simulator
  - Main simulation logic
  - Handles event processing
  - Collects and reports statistics

#### Utils
- **FileReader** (`utils/file_reader.py`): Data input handling
  - Parses CSV records
  - Creates initial event list
  - Validates input data

### Usage

The simulation can be configured and run through `main.py` contained in the `operations research part` directory.

#### Configuration Options

1. **Input File** (`filePath`): 
   - CSV file containing patient records
   - Format: `date,time,duration,patient_type`
   - Example: `2024-01-01,8.5,1.2,"Type 2"`

2. **Scan Times** (`scan_times`): 
   - List of scan durations for each patient type
   - `[Type1_duration, Type2_duration]`
   - Units: hours
   - Example: `[0.8, 1.2]` means:
     - Type 1 patients: 0.8 hours (48 minutes)
     - Type 2 patients: 1.2 hours (72 minutes)

3. **Machine Strategy** (`merged`):
   - `True`: All MRI machines can handle all patient types
   - `False`: Dedicated machines per patient type
   - Affects how patients are assigned to machines

#### Running the Simulation

1. Prepare your input CSV file
2. Configure the simulation parameters
3. Run using:
```bash
python -m operations_research_part.main
```

The simulation will output statistics including:
- Average waiting time in operational hours
- Last scheduled scan date and time
- Last finished scan date and time
- Maximum waiting time in operational hours
- Total overtime used
- Delay statistics:
  - Average delay per customer
  - Maximum delay observed
  - Average delay per day





