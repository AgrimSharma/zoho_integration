
from __future__ import division
from .task_list import *


def task_ux(project):
    query_open = Q(project=project,task_name__icontains='Creative') or \
                 Q(project=project,task_name__icontains='creative',) or \
                 Q(project=project,task_name__icontains='creatives',) or \
                 Q(project=project,task_name__icontains='creatives')
    tasks_open = Tasks.objects.filter(query_open)
    return tasks_open


def task_ui(project):
    query_open = Q(project=project, task_name__icontains='ui') or \
                 Q(project=project,task_name__icontains='UI')

    tasks_open = Tasks.objects.filter(query_open)
    return tasks_open


def task_html(project):
    query_open = Q(project=project, task_name__icontains='HTML') or \
                 Q(project=project,task_name__icontains='html')
    
    tasks_open = Tasks.objects.filter(query_open)
    return tasks_open


def task_api(project):
    query_open = Q(project=project, task_name__icontains='API') or \
                 Q(project=project,task_name__icontains='api')
    tasks_open = Tasks.objects.filter(query_open)
    return tasks_open


def task_bee(project):
    query_open = Q(project=project, task_name__icontains='backend') or \
                 Q(project=project,task_name__icontains='Backend')
    query_re = Q(project=project, task_name__icontains='Redeployment') or \
               Q(project=project,task_name__icontains='redeployment',)
    query_bug = Q(project=project, task_name__icontains='Bug') or \
                Q(project=project,task_name__icontains='bug')


    tasks_open = Tasks.objects.filter(query_open)
    tasks_open_re = Tasks.objects.filter(query_re)
    tasks_open_bug = Tasks.objects.filter(query_bug)
    response = []
    response.extend(tasks_open)
    response.extend(tasks_open_re)
    response.extend(tasks_open_bug)
    return response


def task_qc(project):
    query_open = Q(project=project, task_name__icontains='qc') or \
                 Q(project=project,task_name__icontains='QC')

    tasks_open = Tasks.objects.filter(query_open)
    return tasks_open


def task_uat(project):
    query_open = Q(project=project, task_name__icontains='testing',) or \
                 Q(project=project,task_name__icontains='Testing')

    tasks_open = Tasks.objects.filter(query_open)
    return tasks_open