import argparse
import os
import sys
import yaml
from typing import Any, Dict, List
from . import datasource, todo_file, ui

from .model import Task

def read_config(path: str) -> Dict[str, Any]:
    '''
    Read the config file from the given path and return as a dictionary.
    If the file doesn't exist or is invalid, returns a default configuration.
    '''
    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Validate that the config has the expected structure
        if not isinstance(config, dict):
            print(f"Warning: Config file {path} is not a valid YAML dictionary")
            return {'datasources': []}
            
        if 'datasources' not in config:
            print(f"Warning: Config file {path} doesn't have 'datasources' section")
            config['datasources'] = []
            
        return config
    except FileNotFoundError:
        print(f"Warning: Config file {path} not found, using empty configuration")
        return {'datasources': []}
    except yaml.YAMLError as e:
        print(f"Error parsing config file {path}: {e}")
        return {'datasources': []}
    except Exception as e:
        print(f"Unexpected error reading config file {path}: {e}")
        return {'datasources': []}

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='TODOMD: Task management with markdown files')
    parser.add_argument('file', help='The markdown file to read/write tasks')
    parser.add_argument('--update-datasources', action='store_true', help='Update datasources with task status from the markdown file')
    parser.add_argument('--config', help='Path to config file (default: ~/.config/todomd.yml). Will also use TODOMD_CONFIG env var if set.')
    args = parser.parse_args()

    # Read the config file
    config_path = args.config or os.getenv('TODOMD_CONFIG', '~/.config/todomd.yml')
    config = read_config(os.path.expanduser(config_path))

    # Get todo file path from args
    todo_file_path = args.file

    # Read tasks
    datasources = datasource.from_config(config['datasources'])
    todo_tasks = todo_file.read_tasks(todo_file_path)
    datasource_tasks = datasource.read_tasks(datasources)
    
    # Handle update mode
    if args.update_datasources:
        datasource.update_tasks(datasources, todo_tasks, datasource_tasks)
        sys.exit(0)
   
    # Update the todo file
    tasks_to_add = ui.select_tasks(todo_tasks, datasource_tasks)
    todo_file.update_tasks(todo_file_path, datasource_tasks)
    todo_file.add_tasks(todo_file_path, tasks_to_add)

if __name__ == '__main__':
    main()
