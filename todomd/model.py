from dataclasses import dataclass

@dataclass
class Task:
    id: str
    project: str
    name: str
    completed: bool
