from __future__ import division

import json

import requests
from django.http import HttpResponse
from .models import *
from django.conf import settings
import datetime
from .task_list import *
from django.utils.html import strip_tags


def all_projects(user):

    url = "https://projectsapi.zoho.com/restapi/portal/{}/projects/".format(settings.PORTAL_ID)
    token = Tokens.objects.latest("id")
    access_token = token.access_token
    headers = {
        'authorization': "Bearer {}".format(access_token),
    }
    projects = requests.request("GET", url, headers=headers)
    if projects.status_code in [204, 400, 401, 404]:
        pass
    else:
        projects = projects.json()
        projects_data = projects['projects']
        for p in projects_data:
            try:
                pro = Projects.objects.get(user=user, project_id=p['id'])
            except Exception:
                pro = Projects.objects.create(user=user,
                    project_id=p.get('id', ""),
                    name=p.get('name', ""))
            pro = Projects.objects.get(user=user,project_id=p['id'])
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
            pro.owner_name = owner_name if owner_name else None
            pro.description = strip_tags(p.get('description', ""))
            pro.task_count_open = p.get('task_count', "").get('open', 0)
            pro.task_count_close = p.get('task_count', "").get('closed', 0)
            pro.milestone_count_open = p.get('milestone_count', "").get('open',
                                                                        0)
            pro.milestone_count_close = p.get('milestone_count', "").get(
                'closed', 0)
            pro.status = p.get('status', "")
            pro.created_date_format = datetime.datetime.strptime(created_date,
                                                                 "%m-%d-%Y") if created_date else None
            pro.start_date_format = datetime.datetime.strptime(start_time,
                                                               "%m-%d-%Y") if start_time else None
            pro.folder_url = p.get('link', "").get('folder', "").get("url", "")
            pro.milestone_url = p.get('link', "").get('milestone', "").get(
                "url", "")
            pro.forum_url = p.get('link', "").get('forum', "").get("url", "")
            pro.document_url = p.get('link', "").get('document', "").get("url",
                                                                         "")
            pro.status_url = p.get('link', "").get('status', "").get("url", "")
            pro.event_url = p.get('link', "").get('event', "").get("url", "")
            pro.task_url = p.get('link', "").get('task', "").get("url", "")
            pro.bug_url = p.get('link', "").get('bug', "").get("url", "")
            pro.self_url = p.get('link', "").get('self', "").get("url", "")
            pro.timesheet_url = p.get('link', "").get('timesheet', "").get(
                "url", "")
            pro.user_url = p.get('link', "").get('user', "").get("url", "")
            pro.tasklist_url = p.get('link', "").get('tasklist', "").get("url",
                                                                         "")
            pro.activity_url = p.get('link', "").get('activity', "").get("url",
                                                                         "")
            pro.id_bug_enabled = p.get('id_bug_enabled', "")
            pro.end_date_format = datetime.datetime.strptime(end_time,
                                                             "%m-%d-%Y") if end_time else None
            pro.save()
    return "success"


def project_detail_view(project_id):
    pro = Projects.objects.get(id=project_id)
    current_task, future_date_one_week, past_date_one_week, past_date_two_week=project_task_list_week(project_id)
    task_open = pro.tasks_set.filter(status__in=['Open', 'In Progress']).count()
    task_close = pro.tasks_set.filter(status="Closed").count()
    milestone_close = pro.milestone_set.filter(status="notcompleted").count()
    milestone_open = pro.tasks_set.filter(status="completed").count()
    try:
        percent = task_close/ (task_open + task_close)
    except Exception:
        percent = 0
    data = dict(name=pro.name,
                id=pro.id,
                end_date=pro.end_date_format,
                task_count_open=task_close + task_open,
                milestone_count_open=milestone_open + milestone_close,
                task_count_close=task_close,
                milestone_count_close=milestone_close,
                start_date=pro.start_date_format,
                status=pro.status,
                created_date=pro.created_date_format,
                project_id=pro.project_id,
                current_task=current_task.count(),
                future_date_one_week=future_date_one_week.count(),
                past_date_one_week=past_date_one_week.count(),
                past_date_two_week=past_date_two_week.count(),
                csm=pro.owner_name,
                percent=round(percent * 100, 2)
                )
    return data


def project_list_view(name, status, csm):
    if csm == "all" :
        if status == "all":
            projects = Projects.objects.filter(name__icontains=name)
        elif status == 'open':
            projects = Projects.objects.filter(name__icontains=name, status__in=['active', 'Active'])
        else:
            projects = Projects.objects.filter(name__icontains=name, status__in=['Closed', 'closed'])
    else:
        if status == "all":
            projects = Projects.objects.filter(name__icontains=name, owner_name=csm)
        elif status == 'open':
            projects = Projects.objects.filter(name__icontains=name,
                                               status__in=['active', 'Active'], owner_name=csm)
        else:
            projects = Projects.objects.filter(name__icontains=name,
                                               status__in=['Closed', 'closed'], owner_name=csm)
    response = []
    for pro in projects:
        taks_open = pro.tasks_set.filter(status__in=['Open', 'In Progress', 'open', 'in progress'])
        tasks_close = pro.tasks_set.filter(status__in=['Closed', 'closed'])
        total = len(taks_open) + len(tasks_close)
        current_task, future_date_one_week, past_date_one_week, past_date_two_week = task_list_week_project(pro.id)
        try:
            percent = len(tasks_close) / total
        except Exception:
            percent = 0
        today = datetime.datetime.now().date()
        if pro.status in ["Active",'active'] and pro.end_date_format and pro.end_date_format < today:
            color = "red"
        elif pro.status in ["Active",'active'] and pro.end_date_format == None:
            color = "red"
        elif pro.status in ["closed",'Closed'] and pro.end_date_format == None:
            color = "red"
        else:
            color='green'
        try:
            datetime.datetime.strftime(pro.end_date_format, "%Y-%m-%d")
            if pro.end_date_format < today and pro.status == 'active':
                color = 'red'
            else:
                color = 'green'
            over_due = datetime.datetime.now().date() - pro.end_date_format
        except Exception:
            over_due = None
        milestone_closed = pro.milestone_set.filter(status='notcompleted')
        milestone_open = pro.milestone_set.filter(status='completed')
        data = dict(name=pro.name,
                    id=pro.id,
                    end_date=pro.end_date_format,
                    task_count_open=len(taks_open) + len(tasks_close),
                    milestone_count_open=len(milestone_closed) + len(milestone_open),
                    task_count_close=len(tasks_close),
                    milestone_count_close=len(milestone_closed),
                    start_date=pro.start_date_format,
                    status=pro.status.capitalize(),
                    created_date=pro.created_date_format,
                    project_id=pro.project_id,
                    current_task=current_task,
                    future_date_one_week=future_date_one_week,
                    past_date_one_week=past_date_one_week,
                    past_date_two_week=past_date_two_week,
                    percent=round(percent, 2) * 100,
                    color=color,
                    csm=pro.owner_name,
                    overdue=over_due.days if over_due else None
                    )
        response.append(data)
    return response


def project_list_view_color(name, csm, color):
    today = datetime.datetime.now().date()
    if color == 'red':
        if csm == "all":
            query = Q(name__icontains=name, status__in=['active', 'Active'], end_date_format__lte=today) | Q(name__icontains=name, status__in=['active', 'Active', 'Closed', 'closed'], end_date_format=None)
            projects = Projects.objects.filter(query)
        else:
            query = Q(name__icontains=name,status__in=['active', 'Active'], owner_name=csm, end_date_format__lte=today) | Q(name__icontains=name,status__in=['active', 'Active', 'Closed', 'closed'], owner_name=csm, end_date_format=None)
            projects = Projects.objects.filter(query)
    elif color == 'green':
        if csm == "all":
            query = Q(name__icontains=name, status__in=['Closed', 'closed']) |  Q(name__icontains=name, status__in=['active', 'Active'], end_date_format__gte=today)

            projects = Projects.objects.filter(query).exclude(end_date_format=None)
        else:
            query = Q(name__icontains=name,status__in=['Closed', 'closed'],owner_name=csm)

            projects = Projects.objects.filter(query)
    else:
        week = today + datetime.timedelta(days=7)
        if csm == "all" :
            query = Q(name__icontains=name, status__in=['active', 'Active'], end_date_format__gte=today,end_date_format__lte=week)

            projects = Projects.objects.filter(query)
        else:
            query = Q(name__icontains=name,status__in=['active','Active'],owner_name=csm,end_date_format__gte=today,end_date_format__lte=week)
            projects = Projects.objects.filter(query)
    response = []
    for pro in projects:
        taks_open = pro.tasks_set.filter(status__in=['Open', 'In Progress', 'open', 'in progress'])
        tasks_close = pro.tasks_set.filter(status__in=['Closed', 'closed'])
        total = len(taks_open) + len(tasks_close)
        current_task, future_date_one_week, past_date_one_week, past_date_two_week = task_list_week_project(pro.id)
        try:
            percent = len(tasks_close) / total
        except Exception:
            percent = 0
        today = datetime.datetime.now().date()
        if pro.status in ["Active",'active'] and pro.end_date_format and pro.end_date_format < today:
            color = "red"
        elif pro.status in ["Active",'active'] and pro.end_date_format == None:
            color = "red"
        else:
            color='green'
        try:
            datetime.datetime.strftime(pro.end_date_format, "%Y-%m-%d")
            if pro.end_date_format < today and pro.status == 'active':
                color = 'red'
            else:
                color = 'green'
            over_due = datetime.datetime.now().date() - pro.end_date_format
        except Exception:
            over_due = None
            color = "red"
        milestone_closed = pro.milestone_set.filter(status='notcompleted')
        milestone_open = pro.milestone_set.filter(status='completed')
        data = dict(name=pro.name,
                    id=pro.id,
                    end_date=pro.end_date_format,
                    task_count_open=len(taks_open) + len(tasks_close),
                    milestone_count_open=len(milestone_closed) + len(milestone_open),
                    task_count_close=len(tasks_close),
                    milestone_count_close=len(milestone_closed),
                    start_date=pro.start_date_format,
                    status=pro.status.capitalize(),
                    created_date=pro.created_date_format,
                    project_id=pro.project_id,
                    current_task=current_task,
                    future_date_one_week=future_date_one_week,
                    past_date_one_week=past_date_one_week,
                    past_date_two_week=past_date_two_week,
                    percent=round(percent, 2) * 100,
                    color=color,
                    csm=pro.owner_name,
                    overdue=over_due.days if over_due else None
                    )
        response.append(data)
    return response