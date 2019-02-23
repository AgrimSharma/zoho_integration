from django.db.models import Q
from django.utils.html import strip_tags

from .models import *
import requests
import datetime
from django.conf import settings


def task_filter(tasks):
    response = []
    for t in tasks:
        user_list = t.zohousers_set.all()
        user = ",".join(list(set([u.username for u in user_list])))
        response.append(dict(
            project=t.project.name,
            owner_name=t.owner_name,
            name=t.task_name,
            status=t.status,
            start_date=t.start_date,
            end_date=t.end_date,
            users=user
        ))
    return response


def all_project_task_list(user):
    project = Projects.objects.filter(user=user)
    for p in project:
        if p.tasklist_url == None or p.tasklist_url == "":
            pass
        else:
            token = Tokens.objects.latest("id")
            access_token = token.access_token
            querystring = {"flag": "internal"}

            headers = {
                'authorization': "Bearer {}".format(access_token),
            }
            result = []
            response = requests.request("GET", p.tasklist_url, headers=headers,
                                        params=querystring)
            if response.status_code in [204, 400, 401, 404]:
                pass
            else:
                data = response.json()
                data = data['tasklists']

                for d in data:
                    try:
                        task_list = TaskList.objects.get(user=user, task_list_id=d['id_string'])
                    except Exception:
                        task_list = TaskList.objects.create(user=user, task_list_id=d['id_string'],
                                                            project=p)

                    task_list = TaskList.objects.get(user=user, task_list_id=d['id_string'],
                                                    project=p)

                    try:
                        created_time=datetime.datetime.strptime(d['created_time'], "%Y-%m-%d")
                    except Exception:
                        created_time = None
                    try:
                        milestone = d['milestone']
                        mid=milestone['id']
                    except Exception:
                        mid=None
                    task_list.name=d['name']
                    task_list.view_type=d['flag']
                    task_list.sequence=d['sequence']
                    task_list.created_time=created_time
                    task_list.completed=d['completed']
                    task_list.rolled=d['rolled']
                    task_list.save()
    return


def task_list_project(project_id):
    project = Projects.objects.get(id=project_id)
    data = project.tasklist_set.all()
    result = []
    for d in data:
        tasks = Tasks.objects.filter(tasklist_id=d.task_list_id)
        resp = dict(
            created_time=d.created_time,
            task_name=d.name,
            id_string=d.task_list_id,
            completed=d.completed,
            rolled=d.rolled,
            tasks=filter_tasks(tasks),
            tasks_len=len(tasks)
        )
        result.append(resp)
    return result


def filter_tasks(tasks):
    response = []
    today = datetime.datetime.now().date()
    for t in tasks:
        users = t.zohousers_set.all()
        try:
            datetime.datetime.strftime(t.end_date,"%Y-%m-%d")
            if t.end_date < today and t.status not in ["Closed", "closed"]:
                color="red"
                days_left = today - t.end_date
            elif t.end_date > today and t.status not in ["Closed", "closed"]:
                color = "yellow"
                days_left = t.end_date - today
            else:
                color = "green"
                days_left = t.end_date - today

        except Exception:
            if t.status not in ["Closed", "closed"]:
                color = "red"
            else:
                color = "green"

            days_left = None
        try:
            days_left = days_left.days
        except Exception:
            days_left = 0
        response.append(dict(
            description=strip_tags(t.description)[:20],
            start_date=t.start_date,
            end_date=t.end_date,
            status=t.status,
            subtasks=t.subtasks,
            name=t.task_name,
            id=t.id,
            users=list(set(u.username for u in users)),
            created_person=t.created_person,
            created_time=t.created_time,
            completed=t.completed,
            percent=t.percent_complete,
            color=color,
            days_left=days_left,
            project=t.project
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
