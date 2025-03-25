
import importlib
from typing import Any, Dict, List

from .model import Datasource, Task

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
    # Group tasks by datasource
    tasks_by_datasource = {}
    for task in todo_tasks:
        ds_name = task.datasource
        if ds_name not in tasks_by_datasource:
            tasks_by_datasource[ds_name] = []
        tasks_by_datasource[ds_name].append(task)
    
    # Update each datasource with its tasks
    for ds_name, tasks in tasks_by_datasource.items():
        if ds_name in datasources:
            for task in tasks:
                try:
                    datasources[ds_name].update_task(task)
                except Exception as e:
                    print(f"Error updating task {task.path} in datasource {ds_name}: {e}")


def read_tasks(datasources: Dict[str, Datasource]) -> List[Task]:
    '''
    Read the tasks from the given datasources and return them as a list.
    '''
    all_tasks = []
    
    # Retrieve tasks from each datasource
    for ds_name, datasource in datasources.items():
        try:
            tasks = datasource.get_tasks()
            all_tasks.extend(tasks)
        except Exception as e:
            print(f"Error reading tasks from datasource {ds_name}: {e}")
    
    return all_tasks
