# The airtable datasource
from dataclasses import dataclass
from typing import List

from pyairtable import Table

from ..model import Task, Datasource

@dataclass
class AirtableConnection:
    base: str
    table: str
    view: str
    token: str
    name_field: str
    status_field: str
    completed_value: str
    incompleted_value: str
    datasource: str


def get_tasks(conn: AirtableConnection) -> List[Task]:
    """
    Fetch tasks from Airtable that match the incompleted_value
    """
    # Connect to Airtable
    table = Table(conn.token, conn.base, conn.table)
    
    # Prepare parameters for Airtable query
    params = {}
    
    # Add view parameter if specified
    if conn.view:
        params["view"] = conn.view
    
    # Add formula to filter by status
    formula = f"{{{conn.status_field}}} = '{conn.incompleted_value}'"
    params["formula"] = formula
    
    # Get records using parameters
    records = table.all(**params)
    
    # Convert records to Task objects
    tasks = []
    for record in records:
        record_id = record["id"]
        fields = record["fields"]
        
        # Create task with Airtable record ID as task_id
        task = Task(
            path=record_id,
            name=fields[conn.name_field],
            completed=False,
            datasource=conn.datasource
        )
        tasks.append(task)
    
    return tasks


def update_task(conn: AirtableConnection, task: Task):
    """
    Update task status in Airtable
    """
    # Connect to Airtable
    table = Table(conn.token, conn.base, conn.table)
    
    # Determine the status value based on task completion
    status_value = conn.completed_value if task.completed else conn.incompleted_value
    
    # Update the record
    table.update(task.path, {conn.status_field: status_value})


def from_config(datasource_name: str, config: dict) -> Datasource:
    """
    Create an Airtable datasource from a config dictionary
    """
    conn = AirtableConnection(
        base=config["base"],
        table=config.get("table", "Table 1"),  # Default to "Table 1" if not specified
        view=config.get("view", ""),  # Include view if specified
        token=config["token"],
        name_field=config.get("name_field", "Name"),  # Default to "Name" if not specified
        status_field=config.get("status_field", "Status"),  # Default to "Status" if not specified
        completed_value=config.get("completed_value", "Done"),  # Default to "Done" if not specified
        incompleted_value=config.get("incompleted_value", "Not Done"),  # Default to "Not Done" if not specified
        datasource=datasource_name
    )
    
    return Datasource(
        get_tasks=lambda: get_tasks(conn),
        update_task=lambda task: update_task(conn, task)
    )
