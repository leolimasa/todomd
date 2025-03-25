
import os
import re
from typing import Dict, List, Optional, Tuple

from .model import Task

def _parse_task_line(line: str) -> Optional[Tuple[str, str, bool, str]]:
    """
    Parse a markdown task line into its components
    Returns (task_id, task_name, completed, datasource) or None if not a valid task line
    """
    # Match checkbox markdown format with datasource tag
    # Format: * [ ] Task name @datasource:taskid
    pattern = r"^\*\s+\[([ xX])\]\s+(.+?)\s+@([a-zA-Z0-9_-]+):([a-zA-Z0-9]+)$"
    match = re.match(pattern, line.strip())
    
    if not match:
        return None
    
    checkbox, task_name, datasource, task_id = match.groups()
    completed = checkbox.lower() == "x"
    
    return task_id, task_name, completed, datasource


def _format_task_line(task: Task) -> str:
    """
    Format a task as a markdown line
    """
    checkbox = "x" if task.completed else " "
    return f"* [{checkbox}] {task.name} @{task.datasource}:{task.path}"


def update_tasks(todo_file_path: str, datasource_tasks: List[Task]) -> None:
    '''
    Update the tasks on the todo file with the tasks from the datasources.
    Creates a mapping of (datasource, task_id) to Task objects from datasources,
    then updates matching tasks in the todo file with data from the datasources.
    '''
    # Create expanded file path
    file_path = os.path.expanduser(todo_file_path)
    
    # Create a mapping for quick lookup of tasks by datasource and ID
    task_map = {(task.datasource, task.path): task for task in datasource_tasks}
    
    # If the file doesn't exist, create it with the tasks
    if not os.path.exists(file_path):
        add_tasks(todo_file_path, datasource_tasks)
        return
    
    # Read existing file content
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    # Process each line, updating tasks that match datasource tasks
    updated_lines = []
    for line in lines:
        parsed = _parse_task_line(line.strip())
        
        # If not a task line or task not in datasources, keep line as is
        if not parsed:
            updated_lines.append(line)
            continue
        
        task_id, _, _, datasource = parsed
        task_key = (datasource, task_id)
        
        if task_key in task_map:
            # Update with task from datasources
            task = task_map[task_key]
            updated_lines.append(_format_task_line(task) + "\n")
            # Remove task from map to track which ones were processed
            del task_map[task_key]
        else:
            # Keep the original line if no match in datasources
            updated_lines.append(line)
    
    # Write updated content back to file
    with open(file_path, "w") as f:
        f.writelines(updated_lines)


def add_tasks(todo_file_path: str, tasks: List[Task]) -> None:
    '''
    Add the given tasks to the todo file.
    If the file exists, appends tasks that aren't already in the file.
    If the file doesn't exist, creates it with the given tasks.
    '''
    # Create expanded file path
    file_path = os.path.expanduser(todo_file_path)
    
    # Create a set of existing task IDs to avoid duplicates
    existing_tasks = set()
    
    # If file exists, read existing tasks
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                parsed = _parse_task_line(line.strip())
                if parsed:
                    task_id, _, _, datasource = parsed
                    existing_tasks.add((datasource, task_id))
    
    # Open file in append mode (creates if not exists)
    with open(file_path, "a") as f:
        # Add header if file is new
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            f.write("# Tasks\n\n")
        
        # Add tasks that don't already exist in the file
        for task in tasks:
            task_key = (task.datasource, task.path)
            if task_key not in existing_tasks:
                f.write(_format_task_line(task) + "\n")


def read_tasks(todo_file_path: str) -> List[Task]:
    '''
    Read the todo tasks from the given file path.
    Returns a list of Task objects parsed from the markdown file.
    '''
    # Create expanded file path
    file_path = os.path.expanduser(todo_file_path)
    tasks = []
    
    # If file doesn't exist, return empty list
    if not os.path.exists(file_path):
        return tasks
    
    # Read file and parse tasks
    with open(file_path, "r") as f:
        for line in f:
            parsed = _parse_task_line(line.strip())
            if parsed:
                task_id, task_name, completed, datasource = parsed
                task = Task(
                    path=task_id,
                    name=task_name,
                    completed=completed,
                    datasource=datasource
                )
                tasks.append(task)
    
    return tasks
