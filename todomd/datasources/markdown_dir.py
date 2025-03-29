# The markdown directory datasource
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

from ..model import Task, Datasource
from . import markdown_file
from .. import task


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

            # Read file tasks
            mfile = markdown_file.MarkdownFile(str(file_path), conn.datasource) 
            file_tasks = markdown_file.get_tasks(mfile)
            print(f"File: {file_path}, Tasks: {len(file_tasks)}")

            # Add task paths
            for task in file_tasks:
                task.path = f"{rel_path}"
            tasks.extend(file_tasks)

    except FileNotFoundError:
        # If directory doesn't exist, return empty list
        pass
    
    return tasks

def update_tasks(conn: MarkdownDir, tasks: List[Task]):
    """
    Update task status in the appropriate markdown file.
    Uses the markdown_file datasource to update tasks.
    """
    dir_path = os.path.expanduser(conn.dir)
    by_path = task.group_by_path(tasks)
  
    for file, tasks in by_path.items():
        try: 
            file_path = os.path.join(dir_path, file) # Make the path absolute
            mfile = markdown_file.MarkdownFile(file_path, conn.datasource)
            markdown_file.update_tasks(mfile, tasks)
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
