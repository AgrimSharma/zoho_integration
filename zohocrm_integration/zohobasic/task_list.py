from .models import *
import requests
import datetime


def task_list_project(project_id, portal_id, access_token):
    url = "https://projectsapi.zoho.com/restapi/portal/{portal_id}/" \
          "projects/{project_id}/tasklists/".format(project_id=project_id,
                                                    portal_id=portal_id)

    querystring = {"range": 100}

    headers = {
        'authorization': "Bearer {}".format(access_token),
    }

    response = requests.request("GET", url, headers=headers,
                                params=querystring)
    data = response.json()
    response = []
    if data:
        data = data['tasklists']
    for d in data:
        resp = dict(
            created_time=d['created_time'],
            name=d['name'],
            id_string=d['id_string'],
            completed=d['completed'],
            rolled=d['rolled']
        )
        response.append(resp)
    return response


def project_task_list(project_id):
    project = Projects.objects.get(id=project_id)
    date_today = datetime.datetime.now().date()
    week_day = date_today.weekday()
    begin_date = datetime.datetime.now().date() - datetime.timedelta(
        days=week_day)
    end_date = datetime.datetime.now().date() + datetime.timedelta(
        days=6 - week_day)
    past_date = begin_date - datetime.timedelta(days=7)
    future_date = end_date + datetime.timedelta(days=7)
    current_task = Tasks.objects.filter(project=project,
                                        end_date__gte=begin_date,
                                        end_date__lte=end_date)
    past_task = Tasks.objects.filter(project=project,
                                     end_date__gte=past_date,
                                     end_date__lt=begin_date)
    future_task = Tasks.objects.filter(project=project,
                                       end_date__gte=end_date,
                                       end_date__lte=future_date)

    return current_task,past_task, future_task
