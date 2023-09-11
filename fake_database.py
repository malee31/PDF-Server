# Functions to wrap around a JSON file as if it was a rudimentary database
# Exists only because a real database exists in the project that this repo is a testing bed for
# Actually using a database for this project is unnecessary added complexity
import json
from os import path, sep

fake_database_file = path.join(path.dirname(path.realpath(__file__)), "src%sdatabase.json" % sep)
db = {
    "exists": True,
    "tasks": [],
    "scheduled": []
}


def reload_db():
    if not path.isfile(fake_database_file):
        return

    with open(fake_database_file, "r+") as db_file:
        try:
            db_file_data = json.load(db_file)
            if "exists" in db_file_data:
                global db
                db = {**db, **db_file_data}
        except Exception as e:
            print("Unable to load database file:")
            print(e)

        if "tasks" in db:
            return db["tasks"]
        else:
            return []


def save_db():
    res = json.dumps(db, indent="\t")
    with open(fake_database_file, "w") as db_file:
        db_file.write(res)


reload_db()
save_db()


# Load in a list of all tasks ids, statuses, and results since celery doesn't persist them across reboots
def load_tasks():
    return db["tasks"]


# Cleans up the database by removing uncompleted tasks that aren't in queue anymore
# Optionally clean up tasks that have long expired. This could be a scheduled task instead actually
def clean_tasks():
    save_db()


# Adds a new task to be scheduled or waited on
def add_task(task_id, task_type, task_status, task_result):
    save_db()


# Adds a new task to be completed the next scheduled cycle. There is no removal
def add_scheduled_task(task_type, task_info, start_after_date):
    save_db()


# Update the state of an old task
def update_task(task_id, task_status, task_result):
    save_db()
