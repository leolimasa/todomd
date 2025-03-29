
import importlib
from typing import Any, Dict, List

from .model import Datasource, Task
from . import task

def from_config(datasources_config: Dict[str, Any]) -> Dict[str, Datasource]:
    '''
    Read the datasources from the config and return a dictionary of datasource objects.
    The keys in the dictionary are the datasource names, which are created based on
    the type and optionally the project name or other unique identifier.
    '''
    result = {}
    
    for key, ds_config in datasources_config.items():
        ds_type = ds_config["type"]
        
        try:
            # Import the datasource module dynamically
            # The module name should match the type field in the config
            module_name = f".datasources.{ds_type}"
            module = importlib.import_module(module_name, package="todomd")
            
            # Call the from_config function of the module
            datasource = module.from_config(key, ds_config)
            result[key] = datasource
            
        except (ImportError, AttributeError) as e:
            print(f"Error loading datasource {ds_type}: {e}")
            continue
    
    return result

def _calculate_diff(todo_tasks: Dict[str, List[Task]], ds_tasks: Dict[str, List[Task]]) -> List[Task]:
    '''
    Calculates which tasks have the same path and id in both datasource and todo, and also
    have different completion statuses.
    '''
    changed_tasks = []
    
    common_paths = set(todo_tasks.keys()) & set(ds_tasks.keys())
    print(f"Paths to be updated: {len(common_paths)}")
    print(todo_tasks.keys())
    print(ds_tasks.keys())

    # Iterate through paths that exist in both dictionaries
    for path in common_paths:
        todo_tasks_by_id = task.group_by_id(todo_tasks[path])
        ds_tasks_by_id = task.group_by_id(ds_tasks[path])
        
        # Find tasks with same id but different completion status
        for task_id in set(todo_tasks_by_id.keys()) & set(ds_tasks_by_id.keys()):
            todo_task = todo_tasks_by_id[task_id]
            ds_task = ds_tasks_by_id[task_id]
            
            if todo_task.completed != ds_task.completed:
                # Add the todo task to changed_tasks since that has the updated status
                changed_tasks.append(todo_task)
    
    return changed_tasks

def update_tasks(datasources: Dict[str, Datasource], todo_tasks: List[Task], datasource_tasks: List[Task]) -> None:
    '''
    Update the datasources with the tasks from the todo file.
    Each task will be updated in its corresponding datasource based on the
    task's datasource attribute.
    '''
    print("Updating tasks...")

    # Group tasks by datasource
    todo_tasks_by_datasource = task.group_by_datasource(todo_tasks)
    datasource_tasks_by_datasource = task.group_by_datasource(datasource_tasks)

    # Print the number of tasks in each datasource for debugging
    for ds_name, tasks in todo_tasks_by_datasource.items():
        print(f"Todo tasks for datasource {ds_name}: {len(tasks)}")
    for ds_name, tasks in datasource_tasks_by_datasource.items():
        print(f"Datasource tasks for {ds_name}: {len(tasks)}")

    # Go through each datasource and update tasks that have changed
    for ds_name, ds in datasources.items():
        if ds_name not in todo_tasks_by_datasource or ds_name not in datasource_tasks_by_datasource:
            print(f"No tasks to update for datasource {ds_name}")
            continue
        
        todo_tasks_by_path = task.group_by_path(todo_tasks_by_datasource[ds_name])
        datasource_tasks_by_path = task.group_by_path(datasource_tasks_by_datasource[ds_name])
        diff = _calculate_diff(todo_tasks_by_path, datasource_tasks_by_path)
        print(f"Found {len(diff)} tasks with changed completion status for datasource {ds_name}")
        ds.update_tasks(diff)


def read_tasks(datasources: Dict[str, Datasource]) -> List[Task]:
    '''
    Read the tasks from the given datasources and return them as a list.
    '''
    all_tasks = []
    
    # Retrieve tasks from each datasource
    for ds_name, datasource in datasources.items():
        try:
            tasks = datasource.get_tasks()
            print(f"Read {len(tasks)} tasks from datasource {ds_name}")
            all_tasks.extend(tasks)
        except Exception as e:
            print(f"Error reading tasks from datasource {ds_name}: {e}")
    
    return all_tasks
