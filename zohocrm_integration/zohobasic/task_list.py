from django.db.models import Q
from django.utils.html import strip_tags

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


def filter_tasks(tasks):
    response = []
    for t in tasks:
        response.append(dict(
            description=strip_tags(t.description)[:20],
            start_date=t.start_date,
            end_date=t.end_date,
            status=t.status,
            subtasks=t.subtasks,
            name=t.task_name,
            id=t.id,
            created_person=t.created_person,
            created_time=t.created_time,
            completed=t.completed,
            percent=t.percent_complete,
        ))
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
    cq = Q(project=project, status__in=["In Progress", "Open"]) or Q(project=project,end_date__gte=begin_date,end_date__lte=end_date) or Q(project=project,start_date__gte=begin_date,start_date__lte=end_date)
    # pq = Q(project=project,end_date__lt=begin_date)
    # pq = Q(project=project,start_date__lte=begin_date)
    pq =  Q(project=project, status="Closed") or Q(project=project,end_date__lt=begin_date)
    fq = Q(project=project,end_date__gte=end_date) or Q(project=project,start_date__gte=end_date)
    current_task = Tasks.objects.filter(cq)
    past_task = Tasks.objects.filter(pq)
    future_task = Tasks.objects.filter(fq)
    current_task = filter_tasks(current_task)
    past_task = filter_tasks(past_task)
    future_task = filter_tasks(future_task)

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
    past_date_one = begin_date - datetime.timedelta(days=7)
    past_date_two = past_date_one - datetime.timedelta(days=7)

    current_task = Tasks.objects.filter(project=project,
                                        end_date__gte=begin_date,
                                        end_date__lt=end_date)
    future_date_one_week = Tasks.objects.filter(project=project,
                                                end_date__gte=end_date,
                                                end_date__lt=future_date_one)
    past_date_one_week = Tasks.objects.filter(project=project,
                                              end_date__gte=past_date_one,
                                              end_date__lte=begin_date)

    past_date_two_week = Tasks.objects.filter(project=project,
                                              end_date__gte=past_date_two,
                                              end_date__lte=past_date_one)
    return current_task,future_date_one_week, past_date_one_week, past_date_two_week


def task_list_week_project(project_id):
    project = Projects.objects.get(id=project_id)
    date_today = datetime.datetime.now().date()
    week_day = date_today.weekday()
    begin_date = datetime.datetime.now().date() - datetime.timedelta(
        days=week_day)
    end_date = datetime.datetime.now().date() + datetime.timedelta(
        days=6 - week_day)
    future_date_one = end_date + datetime.timedelta(days=7)
    past_date_one = begin_date - datetime.timedelta(days=7)
    past_date_two = past_date_one - datetime.timedelta(days=7)

    current_task = Tasks.objects.filter(project=project,
                                        end_date__gte=begin_date,
                                        end_date__lt=end_date).count()
    current_task_closed = Tasks.objects.filter(project=project,
                                        end_date__gte=begin_date,
                                        end_date__lt=end_date, status__in=['closed', 'Closed']).count()
    future_date_one_week = Tasks.objects.filter(project=project,
                                                end_date__gte=end_date,
                                                end_date__lt=future_date_one).count()
    future_date_one_week_closed = Tasks.objects.filter(project=project,
                                                end_date__gte=end_date,
                                                end_date__lt=future_date_one,
                                                       status__in=['closed',
                                                                   'Closed']).count()
    past_date_one_week_total = Tasks.objects.filter(project=project,
                                              end_date__gte=past_date_one,
                                              end_date__lte=begin_date).count()
    past_date_one_week_close = Tasks.objects.filter(project=project,
                                                    end_date__gte=past_date_one,
                                                    end_date__lte=begin_date, status__in=['closed', 'Closed']).count()

    past_date_two_week_total = Tasks.objects.filter(project=project,
                                              end_date__gte=past_date_two,
                                              end_date__lte=past_date_one).count()

    past_date_two_week_closed=Tasks.objects.filter(project=project,
                                              end_date__gte=past_date_two,
                                              end_date__lte=past_date_one, status__in=['closed', 'Closed']).count()
    return "{}/{}".format(current_task_closed,current_task), "{}/{}".format(future_date_one_week_closed,future_date_one_week), "{}/{}".format(past_date_one_week_close,past_date_one_week_total), "{}/{}".format(past_date_two_week_closed,past_date_two_week_total)