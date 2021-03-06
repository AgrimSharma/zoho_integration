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


def pull_subtasks(task, user):
    url = task.self_url + "subtasks/"
    token = Tokens.objects.latest("id")
    access_token = token.access_token
    headers = {
            'authorization': "Bearer {}".format(access_token),
            }
    response = requests.request("GET", url, headers=headers)
    if response.status_code in [204, 400, 401, 404]:
        pass
    else:
        data = response.json()
        data = data['tasks']
        for d in data:
            try:
                ta = SubTasks.objects.get(sub_task_id=d['id'])
            except Exception:
                ta = SubTasks.objects.create(sub_task_id=d.get('id', ""),
                                          tasks=task)
                ta.save()
            sub_task = SubTasks.objects.get(sub_task_id=d['id'])
            try:
                end_date = datetime.datetime.strptime(d['end_date'], "%Y-$m-%d")
            except Exception:
                end_date = None
            try:
                start_date = datetime.datetime.strptime(d['start_date'], "%Y-$m-%d")
            except Exception:
                start_date = None
            sub_task.depth=d['depth']
            sub_task.end_date=end_date
            sub_task.priority=d['priority']
            sub_task.percent_complete=d['percent_complete']
            sub_task.duration=d['duration']
            sub_task.name=d['name']
            sub_task.start_date=start_date
            sub_task.completed=d['completed']
            sub_task.created_person=d['created_person']
            sub_task.save()
    return


def all_projects_task(user, name):
    token = Tokens.objects.latest("id")
    if name:
        project = Projects.objects.filter(name__icontains=name)
    else:
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
            querystring = {"range": "300"}

            response = requests.request("GET", url, headers=headers, params=querystring)
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
                    try:
                        own = ZohoUsers.obejcts.filter(tasks=task)
                        owner = [dict(name=o.username, id=o.user_id) for o in
                                 own]

                    except Exception:
                        details = d.get('details', "")
                        owner = []
                        for o in details['owners']:
                            if o['name'] != 'Unassigned':
                                owner.append(dict(name=o['name'], id=o['id']))
                                o = ZohoUsers.objects.create(tasks=task,
                                                             user_id=o['id'],
                                                             username=o[
                                                                 'name'])
                                o.save()
                    timesheet = d['link']['timesheet']['url']
                    self_url = d['link']['self']['url']
                    status = d['status']['name']
                    color_code = d['status']['color_code']
                    percent_complete = d['percent_complete']
                    percent_complete = percent_complete

                    subtasks = d['subtasks']

                    # if subtasks in ["true", "True", True]:
                    #     pull_subtasks(task, user)
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
        users = t.zohousers_set.all()
        time_sheet_count=TimeSheet.objects.filter(task=t).count()
        today = datetime.datetime.now().date()
        if t.status in ["Open", "In Progress", "open",
                        "in progress"] and t.end_date and t.end_date < today:
            status = 'over'
        elif t.status in ["Open", "In Progress",
                          "open"] and t.end_date == None:
            status = 'over'
        elif t.status in ["closed", 'Closed'] and t.end_date == None:
            status = 'closed'
        elif t.status in ["Open", "In Progress", "open",
                          'in progress'] and t.end_date and t.end_date > today:
            status = 'progress'
        else:
            status = 'closed'
        # try:
        #     datetime.datetime.strftime(t.end_date,"%Y-%m-%d")
        #
        #     datetime.datetime.strftime(t.end_date, "%Y-%m-%d")
        #     percent_complete = float(t.percent_complete)
        #     if percent_complete >= 85:
        #         status = "closed"
        #     elif 75.0 <= percent_complete < 85 or t.end_date > today:
        #         status = "progress"
        #     else:
        #         status = "over"
        # except Exception:
        #     status = "over"
            # percent_complete = float(t.percent_complete)

            # if percent_complete >= 85:
            #     status = "closed"
            # elif 75.0 <= percent_complete < 85 or t.end_date > today:
            #     status = "progress"
            # else:
            #     status = "over"
        response.append(dict(
            id=t.id,
            description=strip_tags(t.description) if len(strip_tags(t.description)) < 50 else strip_tags(t.description)[:50] + "...",
            project_id=project.project_id,
            task_list_id=t.tasklist_id,
            task_id=t.task_id,
            start_date=t.start_date,
            end_date=t.end_date,
            status=t.status,
            task_name=t.task_name,
            created_by=t.created_person,
            created_time=t.created_time,
            completed=t.completed,
            percent_complete = t.percent_complete,
            completed_time=t.last_updated_time,
            subtasks=t.subtasks,
            project=t.project,
            owner=",".join(list(set([o.username for o in users]))),
            time_sheet_count=time_sheet_count,
            task_status=status
        ))
    return response
