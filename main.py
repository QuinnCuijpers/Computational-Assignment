from DES import DES

if __name__ == "__main__":
    # start date and end date should be the days themselves
    sim = DES(
        "scanrecords.csv", [0.8, 1.2], merged=False
    )  # estimated based on max length
    sim.run()
    sim.stats()
