from datetime import date, datetime
from todoist_api_python.api import TodoistAPI
import json
import os

API_TOKEN = os.getenv("TODOIST_TOKEN")
PROJECT_ID = "6HhvWp5HFc6j46wq" # "today"

api = TodoistAPI(API_TOKEN)
today = date.today()

try:
    # Fetch tasks filtered by project_id (paginator yields lists)
    all_tasks = []
    for page in api.get_tasks(project_id=PROJECT_ID):
        all_tasks.extend(page)
    
    # Filter tasks with due date today or in the past
    relevant_tasks = [
        task for task in all_tasks
        if task.due and task.due.date <= today
    ]
    
    # Sort tasks: past tasks first (oldest first), then today's tasks
    relevant_tasks.sort(key=lambda task: task.due.date)
    
    # Format tasks with due date annotation for past tasks
    formatted_tasks = []
    for task in relevant_tasks:
        task_date = task.due.date
        content = task.content
        
        # Replace plant emoji with Nerd Font icon
        content = content.replace("🍃", "\ue22f")
        
        # Add recurring icon if task is recurring
        if task.due.is_recurring:
            content += " \uf021"
        
        if task_date < today:
            # Parse the date string and format as "(dd MMM)"
            dt = datetime.fromisoformat(str(task_date))
            date_str = dt.strftime("(%d %b)")
            formatted_tasks.append(f"{content} {date_str}")
        else:
            formatted_tasks.append(content)

    print(f"\nTodos:\n")

    if not formatted_tasks:
        print("🎉 Nothing due today or overdue!")
    else:
        for content in formatted_tasks:
            print(f"- {content}")
    
    # Print tasks as JSON array
    print(f"\nTasks as JSON array:")
    print(json.dumps(formatted_tasks, indent=2, ensure_ascii=False))
            
except Exception as e:
    print("Error fetching tasks:", e)
    import traceback
    traceback.print_exc()

