from functools import wraps
from celery import Celery
import tasks_source as unwrapped_tasks

celery_app = Celery("pdf_tasks", broker="redis://localhost/0", backend="redis://localhost/0")


# Decorator that passes the celery task as `celery_task` to the wrapped function
def celery_wrap(func):
    @celery_app.task(bind=True)
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        self.update_state(state="PROGRESS", meta={"current": 1, "total": 10000, "loading": 999})
        return func(*args, **kwargs, celery_task=self)

    return wrapped


# Wrap and re-export functions for Celery
# Used because Celery makes debugging difficult so code will live outside of Celery and be wrapped into it
bg_extract = celery_wrap(unwrapped_tasks.bg_extract)
