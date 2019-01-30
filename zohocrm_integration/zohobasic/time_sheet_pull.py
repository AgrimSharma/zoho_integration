import requests
from .models import *
import datetime


def all_project_time_sheet():
    token = Tokens.objects.latest("id")
    access_token = token.access_token
    task = Tasks.objects.all()
    for p in task:
        if p.timesheet_url == "" or p.timesheet_url == None:
            pass
        else:
            url = p.timesheet_url
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
