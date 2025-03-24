# TODOMD

A Python command line tool that reads tasks from various datasources, presents them to the user, and adds the selected tasks to a markdown file.

## Installation

```bash
pip install todomd
```

Or using Poetry:

```bash
poetry add todomd
```

## Usage

```bash
# Add tasks to a markdown file
todomd my_tasks.md

# Update datasources with task status from a markdown file
todomd --update my_tasks.md

# Use a custom config file
todomd --config ~/my_todomd_config.yml my_tasks.md
```

## Configuration

TODOMD uses a YAML configuration file located at `~/.config/todomd.yml` by default. Here's an example configuration:

```yaml
datasources:
  - type: airtable
    base: app1234567890abcdef
    view: View 1
    status_field: Status
    incomplete_value: Not Done
    complete_value: Done
    project: Project 1
    
  - type: markdown_file
    file: ~/Documents/tasks.md
    project: Project 2

  - type: markdown_dir
    dir: ~/Documents/Projects
    recursive: false
```

## Features

- Read tasks from multiple datasources
- Group tasks by project
- Interactive task selection interface
- Update task status back to datasources
- Support for Airtable, markdown files, and directories of markdown files

## License

MIT
