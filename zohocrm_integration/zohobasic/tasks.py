import json

from django.http import HttpResponse

from .models import *
import requests
import datetime
from django.utils.html import strip_tags


def project_task(project_id):
    token = Tokens.objects.latest("id")
    project = Projects.objects.get(project_id=project_id)
    access_token = token.access_token
    url = project.task_url
    headers = {
        'authorization': "Bearer {}".format(access_token),
    }

    response = requests.request("GET", url, headers=headers)
    data = response.json()
    response = []
    if data:
        data = data['tasks']
    for d in data:
        try:
            task = Tasks.objects.get(task_id=d['id'])
        except Exception:
            project = Projects.objects.get(project_id=project_id)
            ta = Tasks.objects.create(task_id=d.get('id',""), project=project)
            task = Tasks.objects.get(task_id=d['id'])

        try:
            own = ZohoUsers.obejcts.filter(tasks=task)
            print own
            owner = [dict(name=o.username, id=o.user_id) for o in own]

        except Exception:
            details = d.get('details',"")
            owner = []
            for o in details['owners']:
                if o['name'] != 'Unassigned':
                    owner.append(dict(name=o['name'], id=o['id']))
                    o = ZohoUsers.objects.create(tasks=task, user_id=o['id'], username=o['name'])
                    o.save()

        timesheet=d['link']['timesheet']['url']
        self_url=d['link']['self']['url']

        try:
            status = d['status']['name']
            color_code=d['status']['color_code']
        except Exception:
            status = None
            color_code=None
        try:
            completed_time=d['completed_time']
        except Exception:
            completed_time=None
        try:
            percent_complete=d['percent_complete']
            percent_complete = percent_complete
        except Exception:
            percent_complete=0
        try:
            description = d['description']
        except Exception:
            description = None
        try:
            end_date=d['end_date']
        except Exception:
            end_date = ""
        try:
            start_date=d['start_date']
        except Exception:
            start_date = ""
        try:
            created_time=d['created_time']
        except Exception:
            created_time = ""
        try:
            last_updated_time = d['last_updated_time']
        except Exception:
            last_updated_time = None
        task.milestone_id=d['milestone_id']
        task.self_url=self_url
        task.timesheet_url=timesheet
        task.description=strip_tags(description)
        task.duration=d['duration']
        task.task_id=d['id']
        task.task_key=d['key']
        task.created_person = d['created_person']
        task.created_time = datetime.datetime.strptime(created_time, "%m-%d-%Y") if created_time else None
        task.subtasks=d['subtasks']
        task.work=d['work']
        task.completed=d['completed']
        task.percent_complete=percent_complete
        task.last_updated_time=datetime.datetime.strptime(last_updated_time, "%m-%d-%Y") if last_updated_time else None
        task.completed_time=datetime.datetime.strptime(completed_time, "%m-%d-%Y") if completed_time else None
        task.task_name=d['name']
        task.tasklist_id = d['tasklist']['id']
        task.status=status
        task.color_code=color_code
        task.end_date=datetime.datetime.strptime(end_date, "%m-%d-%Y") if end_date else None
        task.start_date=datetime.datetime.strptime(start_date, "%m-%d-%Y") if start_date else None


        task.save()
        resp = dict(
            project_id=task.project.project_id,
            task_list_id=task.tasklist_id,
            end_date=task.end_date,
            milestone_id=task.milestone_id,
            duration=task.duration,
            task_id=task.task_id,
            start_date=start_date,
            subtasks=task.subtasks,
            task_name=task.task_name,
            description=task.description,
            timesheet=task.timesheet_url,
            owners=owner,
            created_person=task.created_person,
            created_time=task.created_time,
            completed=task.completed,
            percent_complete=task.percent_complete + "%",
            completed_time=task.completed_time,
            status=task.status
        )
        response.append(resp)
    return response


def all_projects_task():
    token = Tokens.objects.latest("id")
    project = Projects.objects.all()
    access_token = token.access_token

    for p in project:
        if p.task_url == None or p.task_url == "":
            pass
        else:
            url = p.task_url
            headers = {
                'authorization': "Bearer {}".format(access_token),
            }

            response = requests.request("GET", url, headers=headers)
            # if data:
            if response.status_code in [204, 400, 401, 404]:
                pass
            else:
                data = response.json()
                data = data['tasks']
                for d in data:
                    try:
                        ta = Tasks.objects.get(task_id=d['id'])
                    except Exception:
                        ta = Tasks.objects.create(task_id=d.get('id', ""),
                                                  project=p)

                    task = Tasks.objects.get(task_id=d['id'])

                    timesheet = d['link']['timesheet']['url']
                    self_url = d['link']['self']['url']

                    # try:
                    status = d['status']['name']
                    # import re
                    # remove_numbers = re.sub("[^a-zA-Z0-9]+", " ",
                    #                         d['name'].strip())
                    # remove_hypen = re.sub("[0-9]{1,}", " ", remove_numbers)

                    color_code = d['status']['color_code']
                    # except Exception:
                    #     status = None
                    #     color_code = None
                    # try:
                    percent_complete = d['percent_complete']
                    percent_complete = percent_complete
                    # except Exception:
                    #     percent_complete = 0
                    try:
                        description = d['description']
                    except Exception:
                        description = None
                    try:
                        end_date = d['end_date']
                    except Exception:
                        end_date = ""
                    try:
                        start_date = d['start_date']
                    except Exception:
                        start_date = ""
                    # try:
                    created_time = d['created_time']
                    # except Exception:
                    #     created_time = ""
                    # try:
                    last_updated_time = d['last_updated_time']
                    # except Exception:
                    #     last_updated_time = None
                    task.milestone_id = d['milestone_id']
                    task.self_url = self_url
                    task.timesheet_url = timesheet
                    task.description = description
                    task.duration = d['duration']
                    task.task_id = d['id']
                    task.task_key = d['key']
                    task.created_person = d['created_person']
                    task.created_time = datetime.datetime.strptime(created_time,
                                                                   "%m-%d-%Y") if created_time else None
                    task.subtasks = d['subtasks']
                    task.work = d['work']
                    task.completed = d['completed']
                    task.percent_complete = percent_complete
                    task.last_updated_time = datetime.datetime.strptime(
                        last_updated_time,
                        "%m-%d-%Y") if last_updated_time else None
                    task.task_name =  d['name']
                    task.tasklist_id = d['tasklist']['id']
                    task.status = status
                    task.color_code = color_code
                    task.end_date = datetime.datetime.strptime(end_date,
                                                               "%m-%d-%Y") if end_date else None
                    task.start_date = datetime.datetime.strptime(start_date,
                                                                 "%m-%d-%Y") if start_date else None

                    task.save()
    return "Success"


def project_open_tasks(project_id):
    project = Projects.objects.get(id=project_id)
    tasks = project.tasks_set.filter(status__in=["Open","In Progress"])
    return tasks


def project_close_tasks(project_id):
    project = Projects.objects.get(id=project_id)
    tasks = project.tasks_set.filter(status__icontains="Closed")
    return tasks


def project_all_tasks(project_id):
    project = Projects.objects.get(id=project_id)
    tasks = project.tasks_set.all()
    response = []
    for t in tasks:
        users = ZohoUsers.objects.filter(tasks=t)
        response.append(dict(
            id=t.id,
            description=strip_tags(t.description) if len(strip_tags(t.description)) < 50 else strip_tags(t.description)[:50] + "...",
            project_id=project.project_id,
            task_list_id=t.tasklist_id,
            task_id=t.task_id,
            start_date=t.start_date,
            end_date=t.end_date,
            status=t.status,
            task_name = t.task_name,
            created_by=t.created_person,
            created_time = t.created_time,
            completed=t.completed,
            percent = t.percent_complete,
            completed_time=t.last_updated_time,
            owner=",".join(list(set([o.username for o in users])))
        ))
    return response
