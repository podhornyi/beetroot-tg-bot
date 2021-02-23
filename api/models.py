from dataclasses import dataclass


@dataclass
class Good:
    name: str
    qtty: int


@dataclass
class GoodList:
    name: str
