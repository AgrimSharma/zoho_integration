import json

from django.http import HttpResponse

from .models import *
import requests
import datetime


def all_projects_milestone(user, name):
    token = Tokens.objects.latest("id")
    if "hdfc" in name:
        project = Projects.objects.filter(name__icontains=name)
    else:
        project = Projects.objects.all()

    access_token = token.access_token

    for p in project:
        if p.milestone_url == "" or p.milestone_url == None:
            pass
        else:
            url = p.milestone_url
            headers = {
                'authorization': "Bearer {}".format(access_token),
            }
            querystring = {"range": "300"}

            response = requests.request("GET", url, headers=headers, params=querystring)
            if response.status_code in [204, 400, 401, 404]:
                pass
            else:
                data = response.json()
                data = data['milestones']
                for d in data:
                    try:
                        end_date = d['end_date']
                    except Exception:
                        end_date = None
                    try:
                        start_date = d['start_date']
                    except Exception:
                        start_date = None
                    try:
                        task = Milestone.objects.get(project=p,
                                                     id_string=d['id_string'])
                    except Exception:
                        miles = Milestone.objects.create(project=p, id_string=d['id_string'])
                    task = Milestone.objects.get(project=p,
                                                 id_string=d['id_string'])

                    task.owner_name=d['owner_name']
                    task.name=d['name']
                    task.status=d['status']
                    task.sequence=d['sequence']
                    task.flag=d['flag']
                    task.id_string=d['id_string']
                    task.end_date = datetime.datetime.strptime(end_date, "%m-%d-%Y") if end_date else None
                    task.last_updated_time=datetime.datetime.strptime(start_date, "%m-%d-%Y") if start_date else None
                    task.save()
    return "s"


def milestone_project_id(project_id):
    project = Projects.objects.get(id=project_id)

    miles_stone = Milestone.objects.filter(project=project)
    if miles_stone:
        return miles_stone
    else:
        token = Tokens.objects.latest("id")
        access_token = token.access_token
        url = project.milestone_url

        headers = {
            'authorization': "Bearer {}".format(access_token)
        }

        portals = requests.request("GET", url, headers=headers)
        if portals.status_code == 204 or portals.status_code == 401:
            response = []
        else:
            data = portals.json()
            if data:
                data = data['milestones']
            for d in data:
                try:
                    end_date = d['end_date']
                except Exception:
                    end_date = None
                try:
                    start_date = d['start_date']
                except Exception:
                    start_date = None
                try:
                    miles = Milestone.objects.get(project=project, id_string=d['id_string'])
                except Exception:
                    miles = Milestone.objects.create(project=project, id_string=d['id_string'])

                task = Milestone.objects.get(project=project, id_string=d['id_string'])
                task.owner_name=d['owner_name']
                task.name=d['name']
                task.status=d['status']
                task.sequence=d['sequence']
                task.flag=d['flag']
                task.id_string=d['id_string']
                task.end_date = datetime.datetime.strptime(end_date, "%m-%d-%Y") if end_date else None
                task.last_updated_time=datetime.datetime.strptime(start_date, "%m-%d-%Y") if start_date else None
                task.save()
            response = Milestone.objects.filter(project=project)
        return response


def project_close_milestone(project_id):
    project = Projects.objects.get(id=project_id)
    milestone = project.milestone_set.filter(status='completed')
    response = []
    for m in milestone:
        tasks = Tasks.objects.filter(milestone_id=m.id_string)
        user = ""
        for t in tasks:
            user_list = t.zohousers_set.all()
            user = ",".join(list(set([u.username for u in user_list])))
        response.append(dict(
            project=project.name,
            owner_name=m.owner_name,
            name=m.name,
            status=m.status,
            start_date=m.start_date,
            end_date=m.end_date,
            sequence=m.sequence,
            flag=m.flag,
            users=user
        ))
    return response


def project_open_milestone(project_id):
    project = Projects.objects.get(id=project_id)
    milestone = project.milestone_set.filter(status='notcompleted')
    response = []
    for m in milestone:
        tasks = Tasks.objects.filter(milestone_id=m.id_string)
        user = ""
        for t in tasks:
            user_list = t.zohousers_set.all()
            user = ",".join(list(set([u.username for u in user_list])))
        response.append(dict(
            project=project.name,
            owner_name=m.owner_name,
            name=m.name,
            status=m.status,
            start_date=m.start_date,
            end_date=m.end_date,
            sequence=m.sequence,
            flag=m.flag,
            users=user,
        ))
    return response


def project_all_milestone(project_id):
    project = Projects.objects.get(id=project_id)
    milestone = project.milestone_set.all()
    response = []
    today =datetime.datetime.now().date()
    for m in milestone:
        tasks = Tasks.objects.filter(milestone_id=m.id_string)
        complete = Tasks.objects.filter(milestone_id=m.id_string, status__in=['Closed','closed']).count()
        # try:
        #     percent = complete / len(tasks)
        # except Exception:
        #     percent = 0
        # if percent >= 85.0:
        #     color = "green"
        # elif 75.0 <= percent < 85.0:
        #     color = "yellow"
        # else:
        #     color = "red"
        if m.status == "notcompleted" and m.end_date > today:
            color = 'yellow'
        elif m.status == "completed":
            color = 'green'
        else:
            color = 'red'

        user = ""
        for t in tasks:
            user_list = t.zohousers_set.all()
            user = ",".join(list(set([str(u.username) for u in user_list])))
        response.append(dict(
            project=project.name,
            owner_name=m.owner_name,
            name=m.name,
            status=m.status,
            start_date=m.start_date,
            end_date=m.end_date,
            sequence=m.sequence,
            flag=m.flag,
            users=user,
            id=m.id,
            task_count=len(tasks),
            color=color

        ))
    return response