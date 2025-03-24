# This tests against a real airtable instance. Make sure AIRTABLE_TOKEN and AIRTABLE_BASE are set in your environment.
import os
import unittest
from unittest.mock import patch, MagicMock

from todomd.datasources.airtable import AirtableConnection, get_tasks, update_task
from todomd.model import Task


class TestAirtable(unittest.TestCase):
    def setUp(self):
        # Get API key from environment or use a placeholder for tests
        self.api_key = os.environ.get("AIRTABLE_TOKEN", "test_api_key")
        
        # Create test connection
        self.conn = AirtableConnection(
            base=os.environ["AIRTABLE_BASE"],
            table="Table 1",
            token=os.environ["AIRTABLE_TOKEN"],
            name_field="Name",
            status_field="Status",
            completed_value="Done",
            incompleted_value="Todo",
            project="Test Project"
        )

    def test_airtable(self, mock_table):
        tasks = get_tasks(self.conn)
       
        # Assertions
        # self.assertEqual(len(tasks), 2)
        # self.assertEqual(tasks[0].id, "rec123456")
        # self.assertEqual(tasks[1].id, "rec789012")
        # self.assertFalse(tasks[0].completed)
        # self.assertEqual(tasks[0].project, "Test Project")
        # 
        # # Verify mock was called correctly
        # mock_table.assert_called_once_with(self.api_key, "test_base", "test_view")
        # mock_instance.all.assert_called_once_with(formula="{Status} = 'Not Done'")
        # TODO



if __name__ == '__main__':
    unittest.main()
