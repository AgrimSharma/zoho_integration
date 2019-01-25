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
        # url = "https://projectsapi.zoho.com/restapi/portal/{portal_id}/projects/{project_id}/tasks/{task_id}/logs/".format(settings.PORTAL_ID,p.project_id, p.task.task_id)
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
                    except Exception:
                        sheet = TimeSheet.objects.create(task=p, project=p.project,
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
    return "s"
