from services.simulator import DES
from pathlib import Path


def main() -> None:
    # merged refers to whether the machines are considered per patient type or not
    sim = DES(
        filePath=Path("scanrecords.csv"),
        scan_times=[0.8, 1.2],  # estimated based on max length
        merged=False,
    )
    sim.run()
    sim.stats()


if __name__ == "__main__":
    main()
