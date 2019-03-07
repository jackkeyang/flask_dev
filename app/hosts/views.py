from . import hosts

@hosts.route('/b')
def index():
    return 'aaaa'