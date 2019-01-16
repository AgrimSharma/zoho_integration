import requests
from .models import *
import datetime
from django.conf import settings


def all_project_time_sheet():
    token = Tokens.objects.latest("id")
    access_token = token.access_token
    project = Projects.objects.all()
    for p in project:
        url = "https://projectsapi.zoho.com/restapi/portal/{portal_id}/projects/{project_id}/tasks/{task_id}/logs/".format(settings.PORTAL_ID,p.project_id, p.task.task_id)
        params = {"bill_status": "all"}
        headers = {
            'authorization': "Bearer {}".format(access_token),
        }
        response = requests.request("GET", url, headers=headers, params=params)

        if response.status_code == 204:
            response = []
        else:
            import pdb;pdb.set_trace()
            response = response.json()
            response = response['timelogs']['tasklogs']
            for r in response:
                try:
                    sheet = TimeSheet.objects.get(task=p.task,
                                                     project=project,
                                                     time_sheet_id=r[
                                                         'id_string'])
                except Exception:
                    sheet = TimeSheet.objects.create(task=p.task, project=project,
                                                 bill_status=r['bill_status'],
                                                 last_modified_date=datetime.datetime.strptime(
                                                     r['last_modified_date'],
                                                     "%m-%d-%Y"),
                                                 time_sheet_id=r['id_string'],
                                                 owner_name=r['owner_name'],
                                                 hours=r['hours'],
                                                 total_minutes=r['total_minutes'],
                                                 hours_display=r['hours_display'],
                                                 notes=r['notes'],
                                                 created_date=datetime.datetime.strptime(
                                                     r['created_date'], "%m-%d-%Y")
                                                 )
                sheet.save()
    time_sheet = TimeSheet.objects.filter(task=p.task)
    return time_sheet


def time_sheet_projects(task_id):
    token = Tokens.objects.latest("id")
    access_token = token.access_token
    task = Tasks.objects.get(id=task_id)

    url = task.timesheet_url
    headers = {
        'authorization': "Bearer {}".format(access_token),
    }
    response = requests.request("GET", url, headers=headers)

    if response.status_code == 204:
        response = []
    else:
        response = response.json()
        response = response['timelogs']['tasklogs']
        for r in response:
            try:
                sheet = TimeSheet.objects.get(task=task, project=task.project,time_sheet_id=r['id_string'])
            except Exception:

                sheet = TimeSheet.objects.create(task=task, project=task.project,
                                                 time_sheet_id=r['id_string'])
                sheet.save()

            tasks = TimeSheet.objects.get(task=task, project=task.project,time_sheet_id=r['id_string'])
            tasks.bill_status = r['bill_status']
            tasks.last_modified_date = datetime.datetime.strptime(
                r['last_modified_date'], "%m-%d-%Y")
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
