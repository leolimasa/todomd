from .model import Task
from typing import List, Dict, Optional

def group_by_datasource(tasks: List[Task]) -> Dict[str, List[Task]]:
    tasks_by_datasource = {}
    for task in tasks:
        ds_name = task.datasource
        if ds_name not in tasks_by_datasource:
            tasks_by_datasource[ds_name] = []
        tasks_by_datasource[ds_name].append(task)
    return tasks_by_datasource

def group_by_id(tasks: List[Task]) -> Dict[str, Task]:
    """
    Group tasks by their id.
    """
    tasks_by_id = {}
    for task in tasks:
        tasks_by_id[task.id] = task
    return tasks_by_id

def group_by_path(tasks: List[Task]) -> Dict[Optional[str], List[Task]]:
    """
    Group tasks by their path.
    """
    tasks_by_path = {}
    for task in tasks:
        if task.path not in tasks_by_path:
            tasks_by_path[task.path] = []
        tasks_by_path[task.path].append(task)
    return tasks_by_path
