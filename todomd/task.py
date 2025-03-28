from .model import Task
from typing import List, Dict

def group_by_datasource(tasks: List[Task]) -> Dict[str, List[Task]]:
    tasks_by_datasource = {}
    for task in tasks:
        ds_name = task.datasource
        if ds_name not in tasks_by_datasource:
            tasks_by_datasource[ds_name] = []
        tasks_by_datasource[ds_name].append(task)
    return tasks_by_datasource

def group_by_path(tasks: List[Task]) -> Dict[str, Task]:
    """
    Group tasks by their path.
    """
    tasks_by_path = {}
    for task in tasks:
        tasks_by_path[task.path] = task
    return tasks_by_path

