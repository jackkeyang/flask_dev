from app.cron_job import test
JOBS = [
    {
        'id': 'test cron job',
        'func': test,
        'args': None,
        'trigger': 'interval',
        'seconds': 10
    }
]
SCHEDULER_API_ENABLED = True
