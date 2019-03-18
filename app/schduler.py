from cron import test
JOBS = [
    {
        'id': 'test cron job',
        'func': test,
        'args': None,
        'trigger': 'interval',
        'seconds': 2
    }
]
SCHEDULER_API_ENABLED = True