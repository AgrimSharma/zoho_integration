import json

from django.http import HttpResponse

from .models import *
import requests
import datetime


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
                tasks_data.append(data)
                for d in tasks_data:
                    try:
                        ta = Tasks.objects.get(task_id=d['id'])
                    except Exception:
                        ta = Tasks.objects.create(task_id=d.get('id', ""),
                                                  project=p)

                    task = Tasks.objects.get(task_id=d['id'])

                    try:
                        # details = d.get('details',"")
                        own = ZohoUsers.objects.filter(tasks=task)
                        owner = [dict(name=o.username, id=o.user_id) for o in own]

                    except Exception:
                        details = d.get('details', "")
                        owner = []
                        for o in details['owners']:
                            if o['name'] != 'Unassigned':
                                owner.append(dict(name=o['name'], id=o['id']))
                                o = ZohoUsers.objects.create(tasks=task,
                                                             user_id=o['id'],
                                                             username=o['name'])
                                o.save()

                    timesheet = d['link']['timesheet']['url']
                    self_url = d['link']['self']['url']

                    try:
                        status = d['status']['name']
                        color_code = d['status']['color_code']
                    except Exception:
                        status = None
                        color_code = None
                    try:
                        completed_time = d['completed_time']
                    except Exception:
                        completed_time = None
                    try:
                        percent_complete = d['percent_complete']
                        percent_complete = percent_complete
                    except Exception:
                        percent_complete = 0
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
                    try:
                        created_time = d['created_time']
                    except Exception:
                        created_time = ""
                    try:
                        last_updated_time = d['last_updated_time']
                    except Exception:
                        last_updated_time = None
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
                    task.completed_time = datetime.datetime.strptime(
                        completed_time, "%m-%d-%Y") if completed_time else None
                    task.task_name = d['name']
                    task.tasklist_id = d['tasklist']['id']
                    task.status = status
                    task.color_code = color_code
                    task.end_date = datetime.datetime.strptime(end_date,
                                                               "%m-%d-%Y") if end_date else None
                    task.start_date = datetime.datetime.strptime(start_date,
                                                                 "%m-%d-%Y") if start_date else None

                    task.save()
    return "Success"
