import requests
from .models import *
from django.conf import settings
import datetime


def all_projects():
    url = "https://projectsapi.zoho.com/restapi/portal/{}/projects/".format(settings.PORTAL_ID)
    token = Tokens.objects.latest("id")
    access_token = token.access_token
    headers = {
        'authorization': "Bearer {}".format(access_token),
    }

    projects = requests.request("GET", url, headers=headers)
    response = []
    # try:
    projects = projects.json()
    if projects:
        projects = projects['projects']
    # except Exception:
    #     projects = Projects.objects.all()
    #     result = []
    #     for detail_project in projects:
    #         data = dict(name=detail_project.name,
    #                     id=detail_project.id,
    #                     end_date=detail_project.end_date_format,
    #                     bugs_count=dict(
    #                         open=detail_project.task_count_open,
    #                         closed=detail_project.task_count_close),
    #                     milestone_count=dict(
    #                         closed=detail_project.milestone_count_open,
    #                         opne=detail_project.milestone_count_close),
    #                     start_date=detail_project.start_date_format,
    #                     status=detail_project.status,
    #                     created_date=detail_project.created_date_format,
    #                     project_id=detail_project.project_id)
    #         result.append(data)
    #     return result

    for p in projects:
        try:
            pro = Projects.objects.get(project_id=p['id'])
        except Exception:
            pros = Projects.objects.create(
                project_id=p.get('id',""),
                name=p.get('name',""))
            pros.save()

            pro = Projects.objects.get(project_id=p['id'])
            try:
                start_time = p.get('start_date', "")
            except Exception:
                start_time = None
            try:
                end_time = p.get('end_date', "")
            except Exception:
                end_time = None

            try:
                created_date = p.get('created_date', "")
            except Exception:
                created_date = None
            try:
                owner_name = p.get('owner_name', "")
            except Exception:
                owner_name = None
            pro.owner_name=owner_name if owner_name else None
            pro.description=p.get('description',"")
            pro.task_count_open=p.get('task_count',"").get('open',0)
            pro.task_count_close=p.get('task_count',"").get('close',0)
            pro.milestone_count_open=p.get('milestone_count',"").get('open',0)
            pro.milestone_count_close=p.get('milestone_count',"").get('close',0)
            pro.status=p.get('status',"")
            pro.created_date_format=datetime.datetime.strptime(created_date, "%m-%d-%Y") if created_date else None
            pro.start_date_format=datetime.datetime.strptime(start_time, "%m-%d-%Y") if start_time else None
            pro.folder_url=p.get('link',"").get('folder',"").get("url","")
            pro.milestone_url=p.get('link',"").get('milestone',"").get("url","")
            pro.forum_url=p.get('link',"").get('forum',"").get("url","")
            pro.document_url=p.get('link',"").get('document',"").get("url","")
            pro.status_url=p.get('link',"").get('status',"").get("url","")
            pro.event_url=p.get('link',"").get('event',"").get("url","")
            pro.task_url=p.get('link',"").get('task',"").get("url","")
            pro.bug_url=p.get('link',"").get('bug',"").get("url","")
            pro.self_url=p.get('link',"").get('self',"").get("url","")
            pro.timesheet_url=p.get('link',"").get('timesheet',"").get("url","")
            pro.user_url=p.get('link',"").get('user',"").get("url","")
            pro.tasklist_url=p.get('link',"").get('tasklist',"").get("url","")
            pro.activity_url=p.get('link',"").get('activity',"").get("url","")
            pro.id_bug_enabled=p.get('id_bug_enabled',"")
            pro.end_date_format=datetime.datetime.strptime(end_time, "%m-%d-%Y") if end_time else None
            pro.save()

        detail_project = Projects.objects.get(project_id=p['id'])

        try:
            bug_count = p['bug_count']
            bug_count_open = bug_count['open']
            bug_count_closed = bug_count['closed']
        except Exception:
            bug_count_closed = None
            bug_count_open=None
        try:
            bug_count = p['milestone_count']
            milestone_count_open = bug_count['open']
            milestone_count_closed = bug_count['closed']
        except Exception:
            milestone_count_closed = None
            milestone_count_open = None

        data = dict(name=detail_project.name,
                    id=detail_project.id,
                    end_date=detail_project.end_date_format,
                    bugs_count=dict(
                        open=bug_count_open,
                        closed=bug_count_closed),
                    milestone_count=dict(
                        closed=milestone_count_closed,
                        opne=milestone_count_open),
                    start_date=detail_project.start_date_format,
                    status=detail_project.status,
                    created_date=detail_project.created_date_format,
                    project_id=detail_project.project_id)
        response.append(data)

    return response


def project_detail_view(project_id):
    pro = Projects.objects.get(id=project_id)
    data = dict(name=pro.name,
                id=pro.id,
                end_date=pro.end_date_format,
                task_count_open=pro.task_count_open,
                milestone_count_open=pro.milestone_count_open,
                task_count_close=pro.task_count_close,
                milestone_count_close=pro.milestone_count_close,
                start_date=pro.start_date_format,
                status=pro.status,
                created_date=pro.created_date_format,
                project_id=pro.project_id)
    return data
