#coding=utf8
from . import hosts
from flask_login import login_required
from ..models import Hosts, Tags ,db, System
from flask import request, render_template, url_for, flash
from sqlalchemy import or_
import json

@hosts.route('/hostlist')
@login_required
def hostlist():
    page = request.args.get('page', 1, type=int)
    pagination = Hosts.query.paginate(page, per_page=10, error_out=False)
    return render_template('hostlist.html', pagination=pagination)

@hosts.route('/hostinfo', methods=['GET', 'POST'])
@login_required
def hostinfo():
    if request.method == 'GET':
        hostid = request.args.get('id')
        host = Hosts.query.filter_by(id=hostid).first_or_404()
        tags = Tags.query.all()
        return render_template('hostinfo.html', host=host.to_json(), tags=tags, hostags=[ i.id for i in host.tags ])
    else:
        data = request.form.to_dict()
        tags = request.form.getlist("tags")
        host = Hosts.query.filter_by(id=data.get("id")).first_or_404()
        host.public_ip = data.get("public_ip")
        host.local_ip = data.get("local_ip")
        for t in tags:
            tag = Tags.query.get(t)
            host.tags.append(tag)
        db.session.commit()
        return json.dumps({'next': url_for('hosts.hostlist')})

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
            flash(u'%s 已存在!'%host.hostname)
            return json.dumps({'next': url_for('hosts.hostadd')})

@hosts.route('/tags', methods=['GET', 'POST'])
@login_required
def tags():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        pagination = Tags.query.paginate(page, per_page=10, error_out=False)
        return render_template('tags.html', pagination=pagination)
    else:
        data = request.form.to_dict()
        tag = Tags.query.filter_by(name=data.get('tagname')).first()
        if not tag:
            tag = Tags(name=data.get('tagname'))
            db.session.add(tag)
            db.session.commit()
            return json.dumps({'status': 'true', 'next': url_for('hosts.tags')})
        else:
            # flash('%s already exists!'%tag.name)
            return json.dumps({'status': 'false', 'message': u'%s 已存在!'%tag.name})

@hosts.route('/deltag', methods=['POST'])
@login_required
def deltag():
    data = request.form.to_dict()
    tag = Tags.query.get(data.get('id'))
    if tag:
        db.session.delete(tag)
        db.session.commit()
    return json.dumps({'next': url_for('hosts.tags')})