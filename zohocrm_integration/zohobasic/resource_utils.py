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


def resource_utilization(request):
    today = datetime.datetime.now()
    year = today.year
    month = today.month
    if month in [4, 6, 9, 11]:
        end_days =  30
    elif month in [1, 3, 5, 7, 8, 10, 12]:
        end_days = 31
    elif month == 2 and is_leap_year(year) == True:
        end_days = 29
    elif month == 2 and is_leap_year(year) == False:
        end_days = 28
    else:
        end_days = 0
    days = today.day
    days_left = today.weekday()
    month_start = today - datetime.timedelta(days=days - 1)
    week_start = today - datetime.timedelta(days=days_left)
    week_end = today + datetime.timedelta(days=days_left)
    month_end = today + datetime.timedelta(days=days)
    time_users = TimeSheet.objects.all().values_list("owner_name")
    user_set = [str(user[0]) for user in set(time_users)]
    week_days = []
    for d in range(days_left):
        if d == 0:
            days = datetime.datetime.strftime(week_start, "%b %d")
        elif days == 31:
            days = datetime.datetime.strftime(week_end, "%b %d")
        else:
            date = week_start + datetime.timedelta(days=d)
            days = datetime.datetime.strftime(date, "%b %d")
        week_days.append(dict(week_date=days))
    response = []
    week_end = week_end + datetime.timedelta(days=1)
    for u in user_set:
        time_sheet_week = TimeSheet.objects.filter(last_modified_date__gte=week_start, last_modified_date__lte=week_end, owner_name=u)
        time_sheet_month = TimeSheet.objects.filter(last_modified_date__gte=month_start, last_modified_date__lte=month_end, owner_name=u)
        time_sheet = []
        for d in range(days_left):
            time_sheet_data = TimeSheet.objects.filter(
                last_modified_date=(week_start + datetime.timedelta(days=d)).date(),
                owner_name=u)
            time_sheet.append(round(float(sum([int(f.total_minutes) for f in time_sheet_data])/60),2))
        user = u
        week_hours = float(sum([int(d.total_minutes) for d in time_sheet_week]) / 60)
        month_logs = float(sum([int(d.total_minutes) for d in time_sheet_month]) / 60)
        response.append(dict(user=" ".join(user.split(".")).upper(),
                             week_hours=round(week_hours,2),
                             days_log=time_sheet,
                             user_name=user, month=month_logs
                             ))
    from operator import itemgetter

    response = sorted(response, key=itemgetter('user'))

    return render(request, 'resource.html',
                  {
                      "week": datetime.datetime.strftime(week_start, "%b %d") + " - " + datetime.datetime.strftime(week_end, "%b %d"),
                      "week_days":week_days,
                      "response": response
                  })
