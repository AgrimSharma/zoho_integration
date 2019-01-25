import json

from django.http import HttpResponse

from .models import *
import requests
import datetime


def resource_utilisation_all():
    timesheet = TimeSheet.objects.all().values_list('owner_name')
    timesheet = [t[0] for t in timesheet]
    users = list(set(timesheet))
    return users
    # tasks = Tasks.objects.all().values_list('created_person')
    # tasks = [t[0] for t in tasks]
    # users = list(set(tasks))
    # response = []
    # for u in users:
    #     task = Tasks.objects.filter(created_person=u, status__in=['Open', 'In Progress'])
    #
    #     response.append(dict(user=u, utilisation=len(task)))
    # return response
