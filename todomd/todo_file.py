
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
    # Format: * [ ] Task name @datasource:taskpath
    pattern = r"^\*\s+\[([ xX])\]\s+(.+?)\s+@([a-zA-Z0-9_-]+):(.+)$"
    match = re.match(pattern, line.strip())
    
    if not match:
        return None
    
    checkbox, task_name, datasource, task_path = match.groups()
    completed = checkbox.lower() == "x"
    
    return task_path, task_name, completed, datasource


def _format_task_line(task: Task) -> str:
    """
    Format a task as a markdown line
    """
    checkbox = "x" if task.completed else " "
    return f"* [{checkbox}] {task.name} @{task.datasource}:{task.path}"


def update_tasks(todo_file_path: str, todo_tasks: List[Task], datasource_tasks: List[Task]) -> None:
    '''
    Update the tasks in the todo file with the latest data from the datasources.
    Uses todo_tasks as the tasks already present in the file.
    Updates completion status of todo_tasks to match datasource_tasks.
    '''
    # Create expanded file path
    file_path = os.path.expanduser(todo_file_path)
    
    # If the file doesn't exist or there are no todo tasks, nothing to update
    if not os.path.exists(file_path) or not todo_tasks:
        return
    
    # Create a mapping for quick lookup of datasource tasks by datasource and ID
    datasource_task_map = {(task.datasource, task.path): task for task in datasource_tasks}
    
    # Track which todo tasks were updated
    updated_tasks = []
    
    # Update todo tasks with status from datasource tasks
    for todo_task in todo_tasks:
        task_key = (todo_task.datasource, todo_task.path)
        
        # If this task exists in datasource tasks, update its status
        if task_key in datasource_task_map:
            datasource_task = datasource_task_map[task_key]
            
            # Update the todo task with datasource values
            todo_task.completed = datasource_task.completed
            todo_task.name = datasource_task.name  # Also update name if changed
            
            # Add to list of updated tasks
            updated_tasks.append(todo_task)
    
    # If no tasks were updated, no need to rewrite file
    if not updated_tasks:
        return
    
    # Read the file content
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Create a map for quick lookup of updated tasks
    updated_task_map = {(task.datasource, task.path): task for task in updated_tasks}
    
    # Process each line, replacing tasks that were updated
    updated_lines = []
    for line in lines:
        parsed = _parse_task_line(line.strip())
        
        # If not a task line, keep as is
        if not parsed:
            updated_lines.append(line)
            continue
        
        task_id, _, _, datasource = parsed
        task_key = (datasource, task_id)
        
        # If this line corresponds to an updated task, replace it
        if task_key in updated_task_map:
            updated_task = updated_task_map[task_key]
            updated_lines.append(_format_task_line(updated_task) + '\n')
        else:
            # Keep original line if no match in updated tasks
            updated_lines.append(line)
    
    # Write updated content back to file
    with open(file_path, 'w') as f:
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
   
    print(f"Reading tasks from: {file_path}")
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
                print(f"Parsed task: {task_id}, Name: {task_name}, Completed: {completed}, Datasource: {datasource}")
    
    return tasks
