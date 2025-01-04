from services.simulator import DES
from pathlib import Path


def main() -> None:
    # Entry point for the simulation

    # Create and configure the Discrete Event Simulator (DES)
    # Parameters:
    # - filePath: path to input CSV file with patient records
    # - scan_times: list of scan durations for different patient types [Type1, Type2]
    # - merged: whether MRI machines can handle both patient types (True)
    #          or are dedicated to specific types (False)
    sim = DES(
        filePath=Path("scanrecords.csv"),
        scan_times=[0.8, 1.2],  # estimated based on max length
        merged=False,
    )

    # Execute the simulation
    sim.run()

    # Display simulation statistics
    sim.stats()


if __name__ == "__main__":
    main()
