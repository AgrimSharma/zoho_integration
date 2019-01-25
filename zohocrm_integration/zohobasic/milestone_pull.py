import json

from django.http import HttpResponse

from .models import *
import requests
import datetime


def all_projects_milestone():
    token = Tokens.objects.latest("id")
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

            response = requests.request("GET", url, headers=headers)
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
