# The markdown directory datasource
import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from todomd import datasource
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
            tasks = markdown_file.get_tasks(mfile)

            # Add project name to task paths
            for task in tasks:
                task.path = f"{rel_path}/{file_no_ext}/{task.path}"

    except FileNotFoundError:
        # If directory doesn't exist, return empty list
        pass
    
    return tasks


def update_task(conn: MarkdownDir, task: Task):
    """
    Update task status in the appropriate markdown file
    Uses the markdown_file datasource to update the task
    """
    dir_path = os.path.expanduser(conn.dir)
    
    # Parse the task path to get the file name and task ID
    path_parts = task.path.split('/')
    task_id = path_parts[-1]  # Last part is the task ID
    
    if conn.recursive and len(path_parts) > 2:
        # If recursive and has more than 2 parts, we have directories
        project_name = path_parts[-2]  # Second-to-last is the project name
        subdir = '/'.join(path_parts[:-2])  # All but the last two parts are the subdirectory
        file_path = os.path.join(dir_path, subdir, f"{project_name}.md")
    else:
        # Not recursive or no subdirectories
        project_name = path_parts[0]  # First part is the project name
        file_path = os.path.join(dir_path, f"{project_name}.md")
    
    try:
        # Create a modified task with just the task ID as the path
        modified_task = Task(
            path=task_id,
            name=task.name,
            completed=task.completed,
            datasource=task.datasource
        )
        
        # Create a MarkdownFile connection and use its update_task function
        mfile = markdown_file.MarkdownFile(file_path, conn.datasource)
        
        # Use the markdown_file update_task function
        markdown_file.update_task(mfile, modified_task)
    except Exception as e:
        print(f"Error updating task in {file_path}: {e}")


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
        update_task=lambda task: update_task(conn, task)
    )
