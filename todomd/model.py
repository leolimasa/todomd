from dataclasses import dataclass
from typing import Callable, List


@dataclass
class Task:
    path: str
    datasource: str
    name: str
    completed: bool


@dataclass
class Datasource:
    get_tasks: Callable[[], List[Task]]
    update_tasks: Callable[[List[Task]], None]
