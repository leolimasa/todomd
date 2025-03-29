# The markdown file datasource
import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from todomd import datasource

from ..model import Task, Datasource
from .. import task

@dataclass
class MarkdownFile:
    file: str
    datasource: str


def _parse_task_line(line: str) -> Optional[Tuple[str, str, bool]]:
    """
    Parse a markdown task line into its components
    Returns (task_id, task_name, completed) or None if not a valid task line
    """
    # Match checkbox markdown format with optional task ID
    pattern = r"^\*\s+\[([ xX])\]\s+(.+?)(?:\s+@tid:([a-zA-Z0-9]+))?$"
    match = re.match(pattern, line.strip())
    
    if not match:
        return None
    
    # Extract components
    checkbox, task_name, task_id = match.groups()
    completed = checkbox.lower() == "x"
    
    # If no task ID, generate one
    if not task_id:
        task_id = generate_task_id(task_name)
    
    return task_id, task_name, completed


def generate_task_id(task_name: str) -> str:
    """
    Generate a task ID by taking the last 5 characters of the SHA256 hash
    """
    task_hash = hashlib.sha256(task_name.encode()).hexdigest()
    return task_hash[-5:]


def get_tasks(conn: MarkdownFile) -> List[Task]:
    """
    Fetch incomplete tasks from a markdown file
    """
    file_path = os.path.expanduser(conn.file)
    tasks = []
    
    try:
        with open(file_path, "r") as f:
            for line in f:
                # Skip if not a task line
                parsed = _parse_task_line(line)
                if not parsed:
                    continue
                
                task_id, task_name, completed = parsed
                
                # Only include incomplete tasks
                if not completed:
                    task = Task(
                        id=task_id,
                        path=None,
                        name=task_name,
                        completed=False,
                        datasource=conn.datasource
                    )
                    tasks.append(task)
    except FileNotFoundError:
        # If file doesn't exist, return empty list
        pass
    
    return tasks

def update_tasks(conn: MarkdownFile, tasks: List[Task]):
    """
    Update task status in markdown file
    Returns True if successful, False otherwise
    """
    file_path = os.path.expanduser(conn.file)
    tasks_by_id = task.group_by_id(tasks)
    
    # Read file content
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    # Find and update the task
    updated = False
    for i, line in enumerate(lines):
        parsed = _parse_task_line(line)
        if not parsed:
            continue
           
        task_id, _, _ = parsed
        if task_id not in tasks_by_id:
            continue

        t = tasks_by_id[task_id]
        # Create updated line with same task_id
        checkbox = "x" if t.completed else " "
        # lines[i] = f"* [{checkbox}] {task.name} @tid:{task.path}\n"
        lines[i] = f"* [{checkbox}] {t.name}\n"
        updated = True
    
    # Write back to file if updated
    if updated:
        with open(file_path, "w") as f:
            f.writelines(lines)
    

def from_config(datasource_name: str, config: dict) -> Datasource:
    """
    Create a MarkdownFile datasource from a config dictionary
    """
    conn = MarkdownFile(
        file=config["file"],
        datasource=datasource_name
    )
    return Datasource(
        get_tasks=lambda: get_tasks(conn),
        update_tasks=lambda tasks: update_tasks(conn, tasks)
    )
