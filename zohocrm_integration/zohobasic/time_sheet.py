import requests
from .models import *
import datetime

# def time_sheet_project(request, project_id):
#     token = Tokens.objects.latest("id")
#     access_token = token.access_token
#     task = Projects.objects.get(project_id=project_id)
#     url = task.timesheet_url
#     headers = {
#         'authorization': "Bearer {}".format(access_token),
#     }
#     response = requests.request("GET", url, headers=headers)
#     return HttpResponse(json.dumps(response.json()))
#     # return render(request, "task_list.html", {"projects": response.json()})
#
#


def time_sheet_projects(task_id):
    token = Tokens.objects.latest("id")
    access_token = token.access_token
    task = Tasks.objects.get(id=task_id)

    sheet = TimeSheet.objects.filter(task=task)
    if sheet:
        return sheet
    else:
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
            sheet = TimeSheet.objects.create(task=task, project=task.project,
                                             bill_status=r['bill_status'],
                                             last_modified_date=datetime.datetime.strptime(r['last_modified_date'],"%m-%d-%Y"),
                                             time_sheet_id=r['id_string'],
                                             owner_name=r['owner_name'],
                                             hours=r['hours'],
                                             total_minutes=r['total_minutes'],
                                             hours_display=r['hours_display'],
                                             notes=r['notes'],
                                             created_date=datetime.datetime.strptime(r['created_date'],"%m-%d-%Y")
                                             )
            sheet.save()
        time_sheet = TimeSheet.objects.filter(task=task)
        return time_sheet
