from .models import *
import requests
import datetime


def all_projects_milestone():
    token = Tokens.objects.latest("id")
    project = Projects.objects.all()
    access_token = token.access_token

    for p in project:
        url = p.milestone_url
        headers = {
            'authorization': "Bearer {}".format(access_token),
        }

        response = requests.request("GET", url, headers=headers)
        data = response.json()
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
        miles = Milestone.objects.all()
        return miles


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
        if portals.status_code == 204:
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