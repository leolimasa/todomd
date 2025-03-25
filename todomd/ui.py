import curses
import curses.panel
from typing import Dict, List, Set, Tuple

from .model import Task

def select_tasks(todo_tasks: List[Task], datasource_tasks: List[Task]) -> List[Task]:
    '''
    Ask the user to select tasks from the datasources to add to the todo file.
    Will not show tasks that are already in the todo file.
    Returns a list of selected tasks.
    '''
    # Create a set of (datasource, task_id) for quick checking of duplicates
    existing_tasks = {(task.datasource, task.path) for task in todo_tasks}
    
    # Filter out tasks that are already in the todo file
    new_tasks = [task for task in datasource_tasks 
                 if (task.datasource, task.path) not in existing_tasks]
    
    # If no new tasks, return empty list
    if not new_tasks:
        return []
    
    # Group tasks by datasource
    tasks_by_datasource: Dict[str, List[Task]] = {}
    for task in new_tasks:
        if task.datasource not in tasks_by_datasource:
            tasks_by_datasource[task.datasource] = []
        tasks_by_datasource[task.datasource].append(task)
    
    # Initialize selected tasks
    selected_tasks: List[Task] = []
    
    # Start curses interface
    curses.wrapper(lambda stdscr: _curses_ui(stdscr, tasks_by_datasource, selected_tasks))
    
    return selected_tasks


def _curses_ui(stdscr, tasks_by_datasource: Dict[str, List[Task]], selected_tasks: List[Task]):
    """
    Curses UI for task selection
    """
    # Clear screen and hide cursor
    stdscr.clear()
    curses.curs_set(0)
    
    # Enable key input
    stdscr.keypad(True)
    
    # Get screen dimensions
    max_y, max_x = stdscr.getmaxyx()
    
    # Set up colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Header
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected item
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Selected task
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Datasource header
    
    # Create a flat list of all tasks with their indices and datasource for display
    display_items: List[Tuple[Task, bool]] = []
    for datasource, tasks in tasks_by_datasource.items():
        # Add datasource header
        for task in tasks:
            # Add task with selection status
            display_items.append((task, False))
    
    # Initialize selection variables
    current_pos = 0  # Current cursor position
    scroll_pos = 0   # Scroll position
    
    # Main loop
    while True:
        stdscr.clear()
        
        # Calculate visible range based on screen size
        visible_items = max_y - 4  # Reserve lines for header and footer
        
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
        
        for i in range(scroll_pos, min(len(display_items), scroll_pos + visible_items)):
            task, is_selected = display_items[i]
            
            # Display datasource header if different from previous
            if current_datasource != task.datasource:
                current_datasource = task.datasource
                if y < max_y - 1:  # Check if we have space
                    stdscr.addstr(y, 2, f"=== {current_datasource} ===", curses.color_pair(4))
                    y += 1
            
            # Skip if we run out of space
            if y >= max_y - 1:
                break
            
            # Prepare selection marker and task line
            marker = "[x]" if is_selected else "[ ]"
            task_line = f"{marker} {task.name}"
            
            # Highlight current position
            if i == current_pos:
                stdscr.addstr(y, 2, task_line[:max_x-4], curses.color_pair(2))
            else:
                attr = curses.color_pair(3) if is_selected else curses.A_NORMAL
                stdscr.addstr(y, 2, task_line[:max_x-4], attr)
            
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
        
        if key == curses.KEY_UP and current_pos > 0:
            current_pos -= 1
        elif key == curses.KEY_DOWN and current_pos < len(display_items) - 1:
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
