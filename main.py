from DES import DES
from datetime import datetime

if __name__ == "__main__":
    # start date and end date should be the days themselves
    sim = DES(
        "scanrecords.csv",
        datetime(2023, 8, 1),
        datetime(2023, 8, 31),
        [1, 1.2],  # estimated based on max length
    )
    sim.run()
    sim.stats()
