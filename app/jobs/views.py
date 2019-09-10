#coding=utf8
from . import jobs
from flask_login import login_required, current_user
from ..models import db, AppJobs, Users, Tags, Apps
from flask import request, render_template, url_for, flash, session
from sqlalchemy import or_
import json
from datetime import datetime

@jobs.route('/appjob', methods=['GET', 'POST'])
@login_required
def appjob():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        if current_user.role == 'ADMIN':
            reviewjobs = AppJobs.query.filter_by(status=0).paginate(page, per_page=10, error_out=False)
            finishjobs = AppJobs.query.filter(or_(AppJobs.status==1, AppJobs.status==2)).paginate(page, per_page=10, error_out=False)
        elif current_user.role == 'USER':
            uid = current_user.id
            reviewjobs = current_user.jobs.filter_by(status=0).paginate(page, per_page=10, error_out=False)
            finishjobs = current_user.jobs.filter(or_(AppJobs.status==1, AppJobs.status==2)).paginate(page, per_page=10, error_out=False)
        return render_template('jobs/appjoblist.html', reviewjobs=reviewjobs, finishjobs=finishjobs)
    else:
        data = request.form.to_dict()
        user = current_user
        appjob = AppJobs.query.filter_by(name=data.get('name')).first()
        if not appjob:
            appjob = AppJobs(**data)
            appjob.users = user
            db.session.add(appjob)
            db.session.commit()
        return json.dumps({'next': url_for('jobs.appjob')})

@jobs.route('/jobinfo', methods=['GET', 'POST'])
@login_required
def jobinfo():
    if request.method == 'GET':
        id = request.args.get('jobid')
        job = AppJobs.query.filter_by(id=id).first_or_404()
        tags = [ tag.to_json() for tag in Tags.query.all() ]
        data = job.to_json()
        data["tags"] = tags
        return json.dumps(data)
    else:
        data = request.form.to_dict()
        appname = data.get("name")
        tag = Tags.query.filter_by(id=data.get("tags")).first_or_404()
        notes = data.get("notes")
        port = data.get("port")

        checkport = Apps.query.filter_by(port=port).first()
        if checkport:
            return json.dumps({'status': 'false', 'message': u'%s 已使用，请更换端口！'%port})
        
        app = Apps(name=appname, port=port, notes=notes)
        app.tag = tag
        db.session.add(app)

        user = Users.query.filter_by(username=data.get("user")).first_or_404()
        user.apps.append(app)
        jobapp = AppJobs.query.filter_by(id=data.get("id")).update({"status": 1, "port": port ,"datetime": datetime.now()})
        db.session.commit()
        
        return json.dumps({'status': 'true', 'next': url_for('hosts.applist')})

@jobs.route("/clock", methods=["POST"])
def jobclock():
    data = request.form.to_dict()
    job = AppJobs.query.filter_by(id=data.get("id")).update({"status": 2, "notes": data.get("notes"),"datetime": datetime.now()})
    db.session.commit()
    return json.dumps({'next': url_for('jobs.appjob')})