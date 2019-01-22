from django.db.models import Q

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
    cq = Q(project=project,end_date__gte=begin_date,end_date__lte=end_date) or Q(project=project,start_date__gte=begin_date,start_date__lte=end_date)
    # pq = Q(project=project,end_date__lt=begin_date)
    # pq = Q(project=project,start_date__lte=begin_date)
    pq =  Q(project=project, status="Closed")
    fq = Q(project=project,end_date__gte=end_date) or Q(project=project,start_date__gte=end_date)
    current_task = Tasks.objects.filter(cq)
    past_task = Tasks.objects.filter(pq)
    future_task = Tasks.objects.filter(fq)
    print len(past_task)
    return current_task,past_task, future_task


def project_task_list_week(project_id):
    project = Projects.objects.get(id=project_id)
    date_today = datetime.datetime.now().date()
    week_day = date_today.weekday()
    begin_date = datetime.datetime.now().date() - datetime.timedelta(
        days=week_day)
    end_date = datetime.datetime.now().date() + datetime.timedelta(
        days=6 - week_day)
    future_date_one = end_date + datetime.timedelta(days=7)
    future_date_two = future_date_one + datetime.timedelta(days=7)
    future_date_three = future_date_two + datetime.timedelta(days=7)

    current_task = Tasks.objects.filter(project=project,
                                        end_date__gte=begin_date,
                                        end_date__lt=end_date)
    future_date_one_week = Tasks.objects.filter(project=project,
                                     end_date__gte=end_date,
                                     end_date__lt=future_date_one)
    future_date_two_week = Tasks.objects.filter(project=project,
                                       end_date__gte=future_date_one,
                                       end_date__lte=future_date_two)

    future_date_three_week = Tasks.objects.filter(project=project,
                                               end_date__gte=future_date_two,
                                               end_date__lte=future_date_three)
    return current_task,future_date_one_week, future_date_two_week, future_date_three_week