from app import celery
from app import db
from celery.utils.log import get_task_logger
from app.models import Hosts, System, Disks
from ansible_tools.ansible_api import Ansible_api
from utils import UpdateHosts

logger = get_task_logger(__name__)

@celery.task(name='host_ping')
def host_ping():
    hosts = ','.join(map(lambda x:x.local_ip, Hosts.query.all())).encode('utf8')
    ansible = Ansible_api(hosts)
    result = ansible.run_adhoc("ping", '', "all")
    unreachable = result.host_unreachable
    failed = result.host_failed
    ok = result.host_ok
    if unreachable or failed:
        un = ["%s"%k for k in unreachable.keys()]
        fild = ["%s"%k for k in failed.keys()]
        ips = un + fild
        Hosts.query.filter(Hosts.local_ip.in_(ips)).update({'status': False}, synchronize_session='fetch')

    if ok:
        ips = [ "%s"%k for k in ok.keys()]
        Hosts.query.filter(Hosts.local_ip.in_(ips)).update({'status': True}, synchronize_session='fetch')
    db.session.commit()

@celery.task(name='host_info')
def host_info():
    hostlist = ','.join(map(lambda x:x.local_ip, Hosts.query.all())).encode('utf8')
    ansible = Ansible_api(hostlist)
    result = ansible.run_adhoc('setup', '', 'all')
    for ip, data in result.host_ok.items():
        system = data.get('ansible_facts').get('ansible_os_family')
        mem = data.get('ansible_facts').get('ansible_memory_mb').get('real').get('total')
        cpus = data.get('ansible_facts').get('ansible_processor_cores')
        hostname = data.get('ansible_facts').get('ansible_fqdn')
        disks = []
        for name, info in data.get('ansible_facts').get('ansible_devices').items():
            if name.startswith('sd'):
                size = int(float(info.get('size').split()[0]))
                disks.append({'name': name, 'size': size})
        
        hostdata = {'hostname': hostname, 
                    'memory': mem, 
                    'cpus': cpus, 
                    'disks': disks, 
                    'local_ip': ip.address, 
                    'system': system
                    }
        UpdateHosts(hostdata)
        