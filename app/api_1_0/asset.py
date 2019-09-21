from . import api
from authentication import auth
from ..models import Hosts, Tags
from flask import jsonify, request
from ..models import db
import json

@api.route('/hosts')
def hosts():
    hosts = Hosts.query.all()
    return jsonify(map(lambda x: x.local_ip, hosts))

@api.route('/ansible/hosts', methods=['PUT'])
def ansibleHosts():
    if request.method == 'PUT':
        # data = request.form.to_dict()
        iplist = request.form.getlist('ips')
        status = request.form.get('status', None)
        print iplist, status
        Hosts.query.filter(Hosts.local_ip.in_(iplist)).update({'status': int(status)}, synchronize_session='fetch')
        db.session.commit()
        return ''

@api.route('/tags')
def tags():
    tags = Tags.query.all()
    tag_hosts = {}
    for t in tags:
        hosts = map(lambda x: x.local_ip, t.host)
        tag_hosts[t.name] = hosts
    return jsonify(tag_hosts)