# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
import datetime
import pytz
from task_list import *
from projects import all_projects, project_detail_view
from tasks import *
from milestone import *
from time_sheet import *

utc=pytz.UTC

scope = "ZohoProjects.portals.READ,ZohoProjects.projects.READ,ZohoProjects.tasklists.READ," \
        "ZohoProjects.tasks.READ,ZohoProjects.timesheets.READ,ZohoProjects.milestones.READ," \
        "ZohoProjects.timesheets.READ"


def portals_data(access_token):
    url = "https://projectsapi.zoho.com/restapi/portals/"

    headers = {
        'authorization': "Bearer {}".format(access_token),
    }

    portals = requests.request("GET", url, headers=headers)
    data = portals.json()
    return data


def token_refresh(refresh):
    url = "https://accounts.zoho.com/oauth/v2/token"

    querystring = {
        "refresh_token": refresh,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "grant_type": "refresh_token"}

    headers = {
        'cache-control': "no-cache",
        'postman-token': "f0a71a13-2ac8-e381-5d83-3958a4a660bf"
    }

    response = requests.request("POST", url, headers=headers,
                                params=querystring)
    data = response.json()
    return data['access_token']


def callback(request):
    code = request.GET.get("code","")
    url = "https://accounts.zoho.com/oauth/v2/token"

    querystring = {
        "code": code,
        "redirect_uri": settings.REDIRECT_URL,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "grant_type": "authorization_code"}

    headers = {
        'cache-control': "no-cache",
        'postman-token': "4627606a-4fa6-897d-01c9-3f41002504e2"
    }

    response = requests.request("POST", url, headers=headers,
                                params=querystring)
    vals = response.json()
    vals['code'] = code
    access = Tokens.objects.latest("id")
    access.access_token = vals['access_token']
    access.refresh_token = vals['refresh_token']
    access.created_at = datetime.datetime.now()
    access.code = code
    # refresh = token_refresh(access.refresh_token)
    # access.access_token = refresh
    # access.created_at = datetime.datetime.now()
    access.save()

    portals = portals_data(access.access_token)

    port = portals.get('portals',"")
    if port:
        projects = all_projects()
        # tasks = all_projects_task()
        # milestone = all_projects_milestone()
        # timesheet= all_project_time_sheet()
        # return HttpResponse(json.dumps(dict(projects=projects, tokens=vals)))
        return render(request, "main.html", {"projects":projects})
        # return HttpResponse(json.dumps(dict(message="Success")))

    else:
        return HttpResponse(json.dumps(dict(error="Auth error")))


def auth_request(request):
    data = "https://accounts.zoho.com/oauth/v2/auth?scope={scope}&client_id=" \
           "{client_id}&response_type=code&access_type=offline&redirect_uri=" \
           "{redirect_url}&prompt=consent".format(scope=scope,
                                                  client_id=settings.CLIENT_ID,
                                                  redirect_url=
                                                        settings.REDIRECT_URL)
    return redirect(data)


def refresh_token(request):
    url = "https://accounts.zoho.com/oauth/v2/token"

    querystring = {"refresh_token": "{{refresh_token}}",
                   "client_id": settings.CLIENT_ID,
                   "client_secret": settings.CLIENT_SECRET,
                   "grant_type": "refresh_token"}

    headers = {
        'cache-control': "no-cache",
        'postman-token': "c6bfd97b-f047-7d68-4e26-831a6ab1e62f"
    }

    response = requests.request("POST", url, headers=headers,
                                params=querystring)

    return HttpResponse(json.dumps(response.json()))


def time_sheet_projects_tasks(request, project_id):
    tasks = time_sheet_projects_task(project_id)
    return render(request, "time_sheet.html", dict(tasks=tasks))


def projects(request):
    project = Projects.objects.all().order_by("name")
    return render(request, "projects.html", {"project": project})


def project_detail(request, project_id):
    project = project_detail_view(project_id)
    return render(request, "project_detail.html", {"project": project})


def time_sheet_task(request, task_id):
    tasks = time_sheet_projects(task_id)
    return render(request, "time_sheet.html", dict(tasks=tasks))
    # return HttpResponse(json.dumps(tasks))


def task_list(request, project_id):
    project = Projects.objects.get(id=project_id)
    milestone = Milestone.objects.filter(project=project)
    if milestone:
        milestone = milestone
    else:
        milestone = milestone_project_id(project_id)
    current_task,past_task,future_task = project_task_list(project_id)
    date_today = datetime.datetime.now().date()

    return render(request, "tasks.html", {
                                        "current_task": current_task,
                                        "past_task": past_task,
                                        "future_task": future_task,
                                        "milestone":milestone,
                                         "date_today": date_today})


def milestone_data(request, project_id):
    mile_stone = milestone_project_id(project_id)
    return render(request, "mile_stone.html", dict(mile_stone=mile_stone))


def task_project(request, project_id):
    project = Projects.objects.get(id=project_id)

    current_task, past_task, future_task = project_task_list(project_id)
    date_today = datetime.datetime.now().date()
    milestone = Milestone.objects.filter(project=project)
    if milestone:
        milestone = milestone
    else:
        milestone = milestone_project_id(project_id)

    return render(request, "tasks/tasks.html", {
        "current_task": current_task,
        "past_task": past_task,
        "future_task": future_task,
        "milestone": milestone,
        "date_today": date_today})