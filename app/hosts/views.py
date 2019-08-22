from . import hosts
from flask_login import login_required
from ..models import Hosts, db
from flask import request, render_template, url_for, flash
from sqlalchemy import or_
import json

@hosts.route('/hostlist')
@login_required
def hostlist():
    page = request.args.get('page', 1, type=int)
    pagination = Hosts.query.paginate(page, per_page=10, error_out=False)
    return render_template('hostlist.html', pagination=pagination)

@hosts.route('/hostadd', methods=['GET', 'POST'])
@login_required
def hostadd():
    if request.method == 'GET':
        return render_template('hostadd.html')
    else:
        data = request.form.to_dict()
        host = Hosts.query.filter(or_(Hosts.hostname==data.get('hostname'), 
                                       Hosts.public_ip==data.get('public_ip'),
                                       Hosts.local_ip==data.get('local_ip'))).first()
        if not host:
            host = Hosts(**data)
            db.session.add(host)
            db.session.commit()
            return json.dumps({'next': url_for('hosts.hostlist')})
        else:
            flash('%s already exists!'%host.hostname)
            return json.dumps({'next': url_for('hosts.hostadd')})