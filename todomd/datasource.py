
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

    # Go through each datasource and update tasks that have changed
    for ds_name, ds in datasources.items():

        if ds_name not in todo_tasks_by_datasource or ds_name not in datasource_tasks_by_datasource:
            print(f"No tasks to update for datasource {ds_name}")
            continue
        
        todo_tasks_by_path = task.group_by_path(todo_tasks_by_datasource[ds_name])
        datasource_tasks_by_path = task.group_by_path(datasource_tasks_by_datasource[ds_name])
        tasks_to_update = []

        for path, cur_task in todo_tasks_by_path.items():
            # Check if the task exists in the datasource and then update if it changed
            if path in datasource_tasks_by_path:
                datasource_task = datasource_tasks_by_path[path]
                if cur_task.completed != datasource_task.completed:
                    tasks_to_update.append(cur_task)

        ds.update_tasks(tasks_to_update)


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
