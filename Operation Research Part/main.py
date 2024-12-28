from DES import DES
from pathlib import Path

if __name__ == "__main__":
    # merged refers to whether the machines are considered per patient type or not
    sim = DES(
        filePath=Path("scanrecords.csv"), scan_times=[0.8, 1.2], merged=False
    )  # estimated based on max length
    sim.run()
    sim.stats()
