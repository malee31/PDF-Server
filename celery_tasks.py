from time import sleep
from celery import Celery
from celery.result import AsyncResult

celery_app = Celery('hello', broker='redis://localhost/0', backend='redis://localhost/0')


@celery_app.task(bind=True)
def hello(self):
    with open("test.txt", "w") as f:
        for i in range(10):
            f.write("Hello World\n")
            f.flush()
            hello.update_state(state="PROGRESS",
                              meta={'current': i, 'total': 10})
            res = AsyncResult(self.request.id)
            print(res.info)
            sleep(1)

    self.update_state(state="Done")
    return 'Complete'
