# The airtable datasource
from dataclasses import dataclass
from typing import List

from pyairtable import Table

from ..model import Task

@dataclass
class AirtableConnection:
    base: str
    table: str
    token: str
    name_field: str
    status_field: str
    completed_value: str
    incompleted_value: str
    project: str


def get_tasks(conn: AirtableConnection) -> List[Task]:
    """
    Fetch tasks from Airtable that match the incompleted_value
    """
    # Connect to Airtable
    table = Table(conn.token, conn.base, conn.table)
    
    # Get records where status is incomplete
    formula = f"{{{conn.status_field}}} = '{conn.incompleted_value}'"
    records = table.all(formula=formula)
    
    # Convert records to Task objects
    tasks = []
    for record in records:
        record_id = record["id"]
        fields = record["fields"]
        
        # Create task with Airtable record ID as task_id
        task = Task(
            id=record_id,
            name=fields[conn.name_field],
            completed=False,
            project=conn.project
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
    table.update(task.id, {conn.status_field: status_value})
