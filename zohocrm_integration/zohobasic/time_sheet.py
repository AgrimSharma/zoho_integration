import json

import requests
from django.http import HttpResponse

from .models import *
import datetime
from django.conf import settings


def all_project_time_sheet():
    token = Tokens.objects.latest("id")
    access_token = token.access_token
    task = Tasks.objects.all()
    for p in task:
        if p.timesheet_url == "" or p.timesheet_url == None:
            pass
        else:
            url = p.timesheet_url
            # params = {"bill_status": "all"}
            headers = {
                'authorization': "Bearer {}".format(access_token),
            }
            response = requests.request("GET", url, headers=headers)

            if response.status_code in [204, 400, 401, 404]:
                pass
            else:
                response = response.json()
                response = response['timelogs']['tasklogs']

                for r in response:
                    try:
                        sheet = TimeSheet.objects.get(task=p,
                                                      project=p.project,
                                                      time_sheet_id=r[
                                                             'id_string'])
                        sheet.bill_status = str(r['bill_status'])
                        sheet.last_modified_date = datetime.datetime.strptime(r['log_date'],"%m-%d-%Y")
                        sheet.owner_name = str(r['owner_name'])
                        sheet.hours = str(r['hours'])
                        sheet.total_minutes = str(r['total_minutes'])
                        sheet.hours_display = str(r['hours_display'])
                        sheet.notes = str(r['notes'])
                        sheet.created_date = datetime.datetime.strptime(r['created_date'], "%m-%d-%Y")
                        sheet.save()
                    except Exception:
                        sheet = TimeSheet.objects.create(task=p, project=p.project,
                                                     bill_status=str(r['bill_status']),
                                                     last_modified_date=datetime.datetime.strptime(r['log_date'], "%m-%d-%Y"),
                                                     time_sheet_id=r['id_string'],
                                                     owner_name=str(r['owner_name']),
                                                     hours=r['hours'],
                                                     total_minutes=r['total_minutes'],
                                                     hours_display=r['hours_display'],
                                                     notes=r['notes'],
                                                     created_date=datetime.datetime.strptime(r['created_date'], "%m-%d-%Y")
                                                     )
                    sheet.save()
    return "s"


def time_sheet_projects(task_id):
    task = Tasks.objects.get(id=task_id)
    time_sheet = TimeSheet.objects.filter(task=task)
    task_name = task.task_name
    return time_sheet, task_name


def time_sheet_projects_task(project_id):
    token = Tokens.objects.latest("id")
    access_token = token.access_token
    project = Projects.objects.get(id=project_id)
    task = project.tasks_set.all()
    for t in task:
        url = t.timesheet_url
        headers = {
            'authorization': "Bearer {}".format(access_token),
        }
        response = requests.request("GET", url, headers=headers)

        if response.status_code == 204 or response.status_code == 401:
            response = []
        else:
            response = response.json()
            response = response['timelogs']['tasklogs']
            for r in response:
                try:
                    sheet = TimeSheet.objects.get(task=t, project=t.project,time_sheet_id=r['id_string'])
                except Exception:

                    sheet = TimeSheet.objects.create(task=t, project=t.project,
                                                     time_sheet_id=r['id_string'])
                    sheet.save()

                tasks = TimeSheet.objects.get(task=t, project=t.project,time_sheet_id=r['id_string'])
                tasks.bill_status = r['bill_status']
                tasks.last_modified_date = datetime.datetime.strptime(
                    r['log_date'], "%m-%d-%Y")
                tasks.owner_name = r['owner_name']
                tasks.hours = r['hours']
                tasks.total_minutes = r['total_minutes']
                tasks.hours_display = r['hours_display']
                tasks.notes = r['notes']
                tasks.created_date = datetime.datetime.strptime(r['created_date'],
                                                          "%m-%d-%Y")
                tasks.save()
    time_sheet = TimeSheet.objects.filter(task=task)
    return time_sheet
