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
    if use_generated_data:
        sim = DES(
            filePath=Path("generated_data.csv"),
            scan_times=[0.58, 1.02],  # estimated based on 95th percentile
            merged=use_merged_mri,
        )
    else:
        sim = DES(
            filePath=Path("scanrecords.csv"),
            scan_times=[0.58, 1.02],  # estimated based on 95th percentile
            merged=use_merged_mri,
        )

    # Execute the simulation
    sim.run()

    # Display simulation statistics
    sim.stats()


if __name__ == "__main__":
    global use_generated_data
    global use_merged_mri
    use_generated_data = True
    use_merged_mri = True
    main()
