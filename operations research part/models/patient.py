from enum import Enum, auto
from typing import Dict


class PatientType(Enum):
    # Enumeration representing different types of patients
    # Using auto() to automatically assign unique values
    TYPE_1 = auto()
    TYPE_2 = auto()

    @classmethod
    def from_string(cls, string: str) -> "PatientType":
        # Converts string representation to PatientType enum
        # Used when reading patient types from input files
        # Example: "Type 1" -> PatientType.TYPE_1
        mapping: Dict[str, "PatientType"] = {"Type 1": cls.TYPE_1, "Type 2": cls.TYPE_2}
        try:
            return mapping[string]
        except KeyError:
            raise ValueError(f"Invalid patient type string: {string}")
