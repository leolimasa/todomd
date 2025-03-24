# TODOMD

## Overview

`todomd` is a python command line program that reads tasks from several datasources, presents them to the user, and then the user chooses which tasks will be added to a specified `.md` file. The `.md` file is provided as the first argument. If no file is provided, it outputs to stdout.

Tasks are presented on a curses interface, and are separated by projects. Once the user selects the tasks they wish to add, they are added to the file with the following format:

```markdown
* [ ] Task name @project:taskid
```

If the task already exists in the file, it will be updated with the task status (completed or not) and any changes to the task name.

If `todomd` is called with the `--update` flag (as in `todomd --update [file]`), then it will update the datasource with the task status. It will then prompt the user if the user wishes to delete the completed lines from the file. 

## Datasources

**airtable**

Connects to the airtable api and reads tasks from a specified base and view. The base and view are specified in the config file. The task id is the airtable record id.
The task status of complete or not complete is identified by a specific field on the record. The config file will specify the field name and the values for complete and not complete. Only fields matching the incomplete value will be presented to the user.

**markdown_file**

Reads tasks from a plain markdown file. Will only read lines where there is a checkbox. The task id is a string with the format `@tid:taskid` where `taskid` is a unique identifier for the task. The string must be the last part of the line. Example:


```markdown
* [ ] Task name @tid:taskid
```

If there is no `@tid:taskid` string, then a new one will be generated and added to the line by taking the last 5 characters of the sha256 hex hash of the task name.

The task status is whether the checkbox is checked or not. Only tasks where the checkbox is unchecked will be presented to the user. The task name is the text after the checkbox.

**markdown_dir**

Read tasks from all markdown files in a directory. Each markdown follows the same rules and format as `markdown_file`. Each file is treated as a separate project, where the project name is the file name without the extension.

## Config file

The config file is stored by default in `~/.config/todomd.yml` and specifies the available datasources. The config file is a yaml file with the following format:

```yaml

datasources:
  - type: airtable
    base: app1234567890abcdef
    view: View 1
    status_field: Status
    incompleted_value: Not Done
    completed_value: Done
    project: Project 1
    
  - type: markdown_file
    file: ~/Documents/tasks.md
    project: Project 2

  - type: markdown_dir
    file: ~/Documents/Projects
    recursive: false
```


