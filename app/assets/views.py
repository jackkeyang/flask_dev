#coding=utf8
from . import assets
from flask_login import login_required
from ..models import Hosts, Tags ,db, System, Apps
from flask import request, render_template, url_for, flash
from sqlalchemy import or_
import json

@assets.route('/hostlist')
@login_required
def hostlist():
    page = request.args.get('page', 1, type=int)
    pagination = Hosts.query.paginate(page, per_page=10, error_out=False)
    return render_template('hostlist.html', pagination=pagination)

@assets.route('/hostinfo', methods=['GET', 'POST'])
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
        print tags
        host = Hosts.query.filter_by(id=data.get("id")).first_or_404()
        host.public_ip = data.get("public_ip")
        host.local_ip = data.get("local_ip")

        tagobjs = [ Tags.query.get(t) for t in tags]
        hosttags = host.tags.all()
        deltags = list(set(hosttags) - set(tagobjs))
        addtags = list(set(tagobjs) - set(hosttags))
        map(lambda t: host.tags.remove(t), deltags)
        map(lambda t: host.tags.append(t), addtags)

        db.session.commit()
        return json.dumps({'next': url_for('asset.hostlist')})

@assets.route('/hostadd', methods=['GET', 'POST'])
@login_required
def hostadd():
    if request.method == 'GET':
        tags = Tags.query.all()
        return render_template('hostadd.html', tags=tags)
    else:
        data = request.form.to_dict()
        tags = request.form.getlist('tags')
        host = Hosts.query.filter(or_(Hosts.hostname==data.get('hostname'), 
                                       Hosts.public_ip==data.get('public_ip'),
                                       Hosts.local_ip==data.get('local_ip'))).first()
        if not host:
            host = Hosts(hostname = data.get('hostname'),
                         public_ip = data.get('public_ip'),
                         local_ip = data.get('local_ip'))
            for t in tags:
                tag = Tags.query.filter_by(id=t).first()
                host.tags.append(tag)
            db.session.add(host)
            db.session.commit()
            return json.dumps({'next': url_for('asset.hostlist')})
        else:
            flash(u'%s 已存在!'%host.hostname)
            return json.dumps({'next': url_for('asset.hostadd')})

@assets.route('/delete', methods=['POST'])
@login_required
def delete():
    data = request.form.to_dict()
    host = Hosts.query.filter_by(id=data.get('id')).first_or_404()
    db.session.delete(host)
    db.session.commit()
    return json.dumps({'next': url_for('asset.hostlist')})

@assets.route('/tags', methods=['GET', 'POST'])
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
            return json.dumps({'status': 'true', 'next': url_for('asset.tags')})
        else:
            # flash('%s already exists!'%tag.name)
            return json.dumps({'status': 'false', 'message': u'%s 已存在!'%tag.name})

@assets.route('/deltag', methods=['POST'])
@login_required
def deltag():
    data = request.form.to_dict()
    tag = Tags.query.filter_by(id=data.get('id')).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    return json.dumps({'next': url_for('asset.tags')})

@assets.route('/apps', methods=['GET'])
@login_required
def applist():
    app = Apps.query.filter_by(id=1).first()
    page = request.args.get('page', 1, type=int)
    pagination = Apps.query.paginate(page, per_page=10, error_out=False)
    return render_template('apps.html', pagination=pagination)

@assets.route('/appinfo', methods=['GET', 'POST'])
@login_required
def appinfo():
    if request.method == 'GET':
        appid = request.args.get('id')
        app = Apps.query.filter_by(id=appid).first_or_404()
        tags = Tags.query.all()
        return render_template('appinfo.html', app=app, tags=tags)
    else:
        data = request.form.to_dict()
        appid = data.get("id")
        app = Apps.query.filter_by(id=data.get("id")).first_or_404()
        tag = Tags.query.filter_by(id=data.get("tags")).first_or_404()
        app.tag = tag
        db.session.commit()
        return json.dumps({'next': url_for('asset.applist')})

@assets.route('/delapp', methods=['POST'])
@login_required
def delapp():
    data = request.form.to_dict()
    appid = data.get("id")
    app = Apps.query.filter_by(id=appid).first_or_404()
    print app.user
    db.session.delete(app)
    db.session.commit()
    return json.dumps({'next': url_for('asset.applist')})