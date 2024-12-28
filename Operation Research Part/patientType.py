from enum import Enum


class PatientType(Enum):
    type1 = 1
    type2 = 2

    @classmethod
    def from_string(cls, string) -> "PatientType":
        mapping: dict[str, PatientType] = {"Type 1": cls.type1, "Type 2": cls.type2}
        return mapping[string]
