# The markdown directory datasource
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

from ..model import Task, Datasource
from . import markdown_file


@dataclass
class MarkdownDir:
    dir: str
    recursive: bool
    datasource: str


def get_tasks(conn: MarkdownDir) -> List[Task]:
    """
    Fetch incomplete tasks from markdown files in a directory
    Each file is treated as a separate project, with the project name
    being the file name without the extension
    """
    dir_path = os.path.expanduser(conn.dir)
    tasks = []
    
    try:
        # Get all markdown files in the directory
        if conn.recursive:
            markdown_files = list(Path(dir_path).glob("**/*.md"))
        else:
            markdown_files = list(Path(dir_path).glob("*.md"))
        
        for file_path in markdown_files:
            # Get relative path for task path construction
            rel_path = file_path.relative_to(dir_path)

            # file name without extension
            file_no_ext = file_path.stem
         
            # Read file tasks
            mfile = markdown_file.MarkdownFile(str(file_path), conn.datasource) 
            file_tasks = markdown_file.get_tasks(mfile)
            print(f"File: {file_path}, Tasks: {len(file_tasks)}")

            # Add project name to task paths
            for task in file_tasks:
                task.path = f"{rel_path}/{task.path}"
                print(task.path)
            tasks.extend(file_tasks)

    except FileNotFoundError:
        # If directory doesn't exist, return empty list
        pass
    
    return tasks

def _tasks_by_file(tasks: List[Task]) -> Dict[str, List[Task]]:
    """
    Helper function to group tasks by their file path
    This will create a dictionary where the keys are directory paths
    and the values are lists of tasks in those directories.
    """
    tasks_by_file = {}
    
    for task in tasks:
        # Extract the directory from the task path
        dir_path = '/'.join(task.path.split('/')[:-1])  # All but the last part
        if dir_path not in tasks_by_file:
            tasks_by_file[dir_path] = []
        tasks_by_file[dir_path].append(task)
    
    return tasks_by_file

def update_tasks(conn: MarkdownDir, tasks: List[Task]):
    """
    Update task status in the appropriate markdown file.
    Uses the markdown_file datasource to update tasks.
    """
    dir_path = os.path.expanduser(conn.dir)
    by_file = _tasks_by_file(tasks)
  
    for file, tasks in by_file.items():
        modified_tasks = []
        for task in tasks:
            # Parse the task path to get the file name and task ID
            path_parts = task.path.split('/')
            task_id = path_parts[-1]  # Last part is the task ID
            modified_task = Task(
                path=task_id,
                name=task.name,
                completed=task.completed,
                datasource=task.datasource
            )
            modified_tasks.append(modified_task)

        try: 
            # Create a MarkdownFile connection and use its update_task function
            file_path = os.path.join(dir_path, file) # Make the path absolute
            mfile = markdown_file.MarkdownFile(file_path, conn.datasource)
            markdown_file.update_tasks(mfile, modified_tasks)
        except Exception as e:
            print(f"Error updating tasks in {file}: {e}")


def from_config(datasource_name: str, config: dict) -> Datasource:
    """
    Create a MarkdownDir datasource from a config dictionary
    """
    conn = MarkdownDir(
        dir=config["dir"],
        recursive=config.get("recursive", False),
        datasource=datasource_name
    )
    return Datasource(
        get_tasks=lambda: get_tasks(conn),
        update_tasks=lambda tasks: update_tasks(conn, tasks)
    )
