import curses
import curses.panel
import os.path
from typing import Dict, List, Set, Tuple, Optional

from .model import Task
from . import task

def select_tasks(todo_tasks: List[Task], datasource_tasks: List[Task]) -> List[Task]:
    '''
    Ask the user to select tasks from the datasources to add to the todo file.
    Will not show tasks that are already in the todo file.
    Returns a list of selected tasks.
    '''
    # Create a set of (datasource, task_id) for quick checking of duplicates
    existing_tasks = {(task.datasource, task.path, task.id) for task in todo_tasks}
    
    # Filter out tasks that are already in the todo file
    new_tasks = [task for task in datasource_tasks 
                 if (task.datasource, task.path, task.id) not in existing_tasks]

    # Filter out tasks that are completed
    new_tasks = [task for task in new_tasks if not task.completed]
    
    # If no new tasks, return empty list
    if not new_tasks:
        return []

    # Group tasks by datasource and path for hierarchical display
    tasks_by_datasource = task.group_by_datasource(new_tasks)
    tasks_by_datasource_and_path = {ds: task.group_by_path(items) for ds, items in tasks_by_datasource.items()}
   
    # Initialize selected tasks
    selected_tasks: List[Task] = []

    # Start curses interface
    curses.wrapper(lambda stdscr: _curses_ui(stdscr, tasks_by_datasource_and_path, selected_tasks))
    
    return selected_tasks


def _curses_ui(stdscr, tasks_by_datasource_and_path: Dict[str, Dict[Optional[str], List[Task]]], selected_tasks: List[Task]):
    """
    Curses UI for task selection with hierarchical organization by datasource and path
    """
    # Clear screen and hide cursor
    stdscr.clear()
    curses.curs_set(0)
    
    # Enable key input
    stdscr.keypad(True)
    
    # Set up colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)    # Header
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Selected item
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Selected task
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Datasource header
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Directory header
    
    # Create a flat list of all tasks with their selection status for display
    display_items: List[Tuple[Task, bool]] = []
    
    # Flatten the hierarchical structure for display
    for _, paths in tasks_by_datasource_and_path.items():
        for _, tasks in paths.items():
            for task in tasks:
                display_items.append((task, False))
    
    # Initialize selection variables
    current_pos = 0  # Current cursor position
    scroll_pos = 0   # Scroll position
        
    stdscr.clear()

    # Main loop
    while True:
        # Clear the entire screen to prevent ghosting
        stdscr.clear()
        
        # Get screen dimensions
        max_y, max_x = stdscr.getmaxyx()
        
        # Calculate visible range based on screen size
        visible_items = max_y - 6  # Reserve lines for header and footer
        
        # Adjust scroll position if needed
        if current_pos < scroll_pos:
            scroll_pos = current_pos
        elif current_pos >= scroll_pos + visible_items:
            scroll_pos = current_pos - visible_items + 1
        
        # Draw header
        header = "TODOMD - Select Tasks"

        # Avoid writing to the right edge of the screen
        header_text = header.center(max_x-1)
        instructions = "Press SPACE to select a task, ENTER to confirm, q to quit"
        instructions_text = instructions.center(max_x-1)
        
        stdscr.addstr(0, 0, header_text, curses.color_pair(1))
        stdscr.addstr(1, 0, instructions_text)
        
        # Draw tasks
        y = 3  # Start drawing from line 3
        current_datasource = None
        current_path = None
        
        # Clear all task lines to prevent ghosting
        for clear_y in range(3, max_y-1):
            stdscr.addstr(clear_y, 0, " " * (max_x-1))
        
        for i in range(scroll_pos, min(len(display_items), scroll_pos + visible_items)):
            task, is_selected = display_items[i]
            
            # Display datasource header if different from previous
            if current_datasource != task.datasource:
                current_datasource = task.datasource
                if y < max_y - 1:  # Check if we have space
                    stdscr.addstr(y, 2, f"  {current_datasource}".ljust(max_x-4), curses.color_pair(4))
                    y += 1
            
            # Display directory header if different from previous and not empty
            if task.path is not None and current_path != task.path:
                current_path = task.path
                if y < max_y - 1:  # Check if we have space
                    stdscr.addstr(y, 4, f"  {task.path}".ljust(max_x-6), curses.color_pair(5))
                    y += 1
            
            # Skip if we run out of space
            if y >= max_y - 1:
                break
            
            # Prepare selection marker and task line
            marker = "[x]" if is_selected else "[ ]"
            # Display project name (last directory or filename) with task name
            task_line = f"{marker} {task.name}"
            
            # Ensure the line is padded to clear any previous content
            padded_line = task_line.ljust(max_x-4)
            
            # Determine indentation level based on structure
            indent = 6 if task.path is not None else 4
            
            # Highlight current position
            if i == current_pos:
                stdscr.addstr(y, indent, padded_line, curses.color_pair(2))
            else:
                attr = curses.color_pair(3) if is_selected else curses.A_NORMAL
                stdscr.addstr(y, indent, padded_line, attr)
            
            y += 1
        
        # Draw footer
        footer = f"Selected: {sum(1 for _, selected in display_items if selected)} of {len(display_items)} tasks"
        # Avoid writing to the bottom-right corner of the screen (max_y-1, max_x-1)
        # which can cause an error in curses
        footer_text = footer.center(max_x-1)  # Leave one character of space at the end
        stdscr.addstr(max_y-1, 0, footer_text, curses.color_pair(1))
        
        # Refresh screen
        stdscr.refresh()
        
        # Handle keys
        key = stdscr.getch()
       
        if (key == curses.KEY_UP or key == ord('k')) and current_pos > 0:
            current_pos -= 1
        elif (key == curses.KEY_DOWN or key == ord('j')) and current_pos < len(display_items) - 1:
            current_pos += 1
        elif key == ord(' '):  # Space to toggle selection
            if current_pos < len(display_items):
                task, is_selected = display_items[current_pos]
                display_items[current_pos] = (task, not is_selected)
        elif key == 10:  # Enter to confirm
            # Add selected tasks to result
            for task, is_selected in display_items:
                if is_selected:
                    selected_tasks.append(task)
            return
        elif key == ord('q') or key == 27:  # q or ESC to quit
            return
