from enum import Enum


class PatientType(Enum):
    TYPE_1 = 1
    TYPE_2 = 2

    @classmethod
    def from_string(cls, string) -> "PatientType":
        mapping: dict[str, PatientType] = {"Type 1": cls.TYPE_1, "Type 2": cls.TYPE_2}
        return mapping[string]
