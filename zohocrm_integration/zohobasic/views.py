# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
import pytz
from django.views.decorators.csrf import csrf_exempt
from resource_utils import *
from projects import *
from tasks import *
from milestone import *
from time_sheet import *
from django.contrib.auth.models import User

utc=pytz.UTC

scope = "ZohoProjects.portals.READ,ZohoProjects.projects.READ,ZohoProjects.tasklists.READ," \
        "ZohoProjects.tasks.READ,ZohoProjects.timesheets.READ,ZohoProjects.milestones.READ," \
        "ZohoProjects.timesheets.READ"


def portals_data(access_token):
    url = "https://projectsapi.zoho.com/restapi/portals/"

    headers = {
        'authorization': "Bearer {}".format(access_token),
    }

    portals = requests.request("GET", url, headers=headers)
    data = portals.json()
    return data


def token_refresh(refresh):
    url = "https://accounts.zoho.com/oauth/v2/token"

    querystring = {
        "refresh_token": refresh,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "grant_type": "refresh_token"}

    headers = {
        'cache-control': "no-cache",
        'postman-token': "f0a71a13-2ac8-e381-5d83-3958a4a660bf"
    }

    response = requests.request("POST", url, headers=headers,
                                params=querystring)
    data = response.json()
    return data['access_token']


def callback(request):
    code = request.GET.get("code","")
    url = "https://accounts.zoho.com/oauth/v2/token"

    querystring = {
        "code": code,
        "redirect_uri": settings.REDIRECT_URL,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "grant_type": "authorization_code"}

    headers = {
        'cache-control': "no-cache",
        'postman-token': "4627606a-4fa6-897d-01c9-3f41002504e2"
    }

    response = requests.request("POST", url, headers=headers,
                                params=querystring)
    try:
        vals = response.json()
        vals['code'] = code
        access = Tokens.objects.latest("id")
        access.access_token = vals['access_token']
        # access.refresh_token = vals['refresh_token']
        access.created_at = datetime.datetime.now()
        access.code = code
        # refresh = token_refresh(access.refresh_token)
        # access.access_token = refresh
        # access.created_at = datetime.datetime.now()
        access.save()
        port = settings.PORTAL_ID
        
    except Exception:

        port = settings.PORTAL_ID

    if port:
        # projects = all_projects()
        # tasks = all_projects_task()
        # milestone = all_projects_milestone()
        # timesheet= all_project_time_sheet()
        return redirect("/projects_pull/")
    else:
        return HttpResponse(json.dumps(dict(error="Auth error")))


def auth_request(request):
    data = "https://accounts.zoho.com/oauth/v2/auth?scope={scope}&client_id=" \
           "{client_id}&response_type=code&access_type=offline&redirect_uri=" \
           "{redirect_url}&prompt=consent".format(scope=scope,
                                                  client_id=settings.CLIENT_ID,
                                                  redirect_url=
                                                        settings.REDIRECT_URL)
    return redirect(data)


def refresh_token(request):
    url = "https://accounts.zoho.com/oauth/v2/token"

    querystring = {"refresh_token": "{{refresh_token}}",
                   "client_id": settings.CLIENT_ID,
                   "client_secret": settings.CLIENT_SECRET,
                   "grant_type": "refresh_token"}

    headers = {
        'cache-control': "no-cache",
        'postman-token': "c6bfd97b-f047-7d68-4e26-831a6ab1e62f"
    }

    response = requests.request("POST", url, headers=headers,
                                params=querystring)

    return HttpResponse(json.dumps(response.json()))


def time_sheet_projects_tasks(request, project_id):
    tasks = time_sheet_projects_task(project_id)
    return render(request, "time_sheet.html", dict(tasks=tasks))


def projects(request):
    user = request.user
    try:
        user = User.objects.get(username=user.username)
        project = Projects.objects.all().order_by("name")
        return render(request, "projects.html", {"project": project})
    except Exception:
        return redirect("/")


def projects_grantt(request):
    # user = request.user
    # try:
    #     user = User.objects.get(username=user.username)
    project = Projects.objects.filter(start_date_format__year__gte=
                                      datetime.datetime.now().year - 1).order_by("name")
    response = []
    for p in project:
        import re
        try:
            datetime.datetime.strftime(p.start_date_format, "%m-%d-%Y")
            start_date_month = p.start_date_format.month
            start_date_year = p.start_date_format.year
            start_date_date = p.start_date_format.day
        except Exception:
            start_date_month = datetime.datetime.now().month
            start_date_year = datetime.datetime.now().year
            start_date_date = datetime.datetime.now().day
        try:
            datetime.datetime.strftime(p.end_date_format, "%m-%d-%Y")
            end_date_month = p.end_date_format.month
            end_date_year = p.end_date_format.year
            end_date_date = p.end_date_format.day
        except Exception:
            end_date_month = datetime.datetime.now().month
            end_date_year = datetime.datetime.now().year
            end_date_date = datetime.datetime.now().day
        try:
            percent = p.task_count_close / (
                        p.task_count_close + p.task_count_open)
        except Exception:
            percent = 0
        tasks = p.tasks_set.all()
        task_data = []
        for t in tasks:
            try:
                end_date = datetime.datetime.strftime(t.end_date, "%Y-%m-%d")
            except Exception:
                end_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
            try:
                start_date = datetime.datetime.strftime(t.start_date,
                                                        "%Y-%m-%d")
            except Exception:
                start_date = datetime.datetime.strftime(p.start_date_format, "%Y-%m-%d")
            current = datetime.datetime.now()
            ends = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            if ends >= current and t.status in ["Open", "In Progress"]:
                color = "#ffbf00"
            elif ends <= current and t.status in ["Open", "In Progress"]:
                color = "#FF0000"
            else:
                color = "#008000"
            task_data.append(dict(task=t.task_name,
                                  start=start_date,
                                  end=end_date,
                                  color=color
                                  ))
        remove_numbers = re.sub("[^a-zA-Z0-9]+"," ", p.name.strip())
        remove_hypen = re.sub("[0-9]{1,}"," ", remove_numbers)
        if len(tasks) > 0:

            response.append(dict(name=remove_hypen,
                                 start_date_month=start_date_month,
                                 start_date_year=start_date_year,
                                 start_date_date=start_date_date,
                                 end_date_month=end_date_month,
                                 end_date_year=end_date_year,
                                 end_date_date=end_date_date,
                                 project_id=p.project_id,
                                 status=p.status,
                                 percent=percent * 100,
                                 tasks=task_data))

    return HttpResponse(json.dumps(dict(data=response)))
    # except Exception:
    #     return redirect("/")


def project_detail(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = project_detail_view(project_id)

        return render(request, "project_detail.html", {"project": project})
    else:
        return redirect("/")


def time_sheet_task(request, task_id):
    user = request.user
    if user.is_authenticated():
        tasks,task_name = time_sheet_projects(task_id)
        return render(request, "time_sheet.html", dict(tasks=tasks,
                                                       task_name=task_name))
    # return HttpResponse(json.dumps(tasks))
    else:
        return redirect("/")


def task_list(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        milestone = Milestone.objects.filter(project=project)
        if milestone:
            milestone = milestone
        else:
            milestone = milestone_project_id(project_id)
        current_task,past_task,future_task = project_task_list(project_id)
        date_today = datetime.datetime.now().date()

        return render(request, "tasks.html", {
                                            "current_task": current_task,
                                            "past_task": past_task,
                                            "future_task": future_task,
                                            "milestone":milestone,
                                             "date_today": date_today,
                                            "name": project.name})
    else:
        return redirect("/")


def milestone_data(request, project_id):
    user = request.user
    if user.is_authenticated():
        mile_stone = milestone_project_id(project_id)
        return render(request, "mile_stone.html", dict(mile_stone=mile_stone))
    else:
        return redirect("/")


def task_project(request, project_id):
    project = Projects.objects.get(id=project_id)

    current_task, past_task, future_task = project_task_list(project_id)
    date_today = datetime.datetime.now().date()
    milestone = Milestone.objects.filter(project=project)
    if milestone:
        milestone = milestone
    else:
        milestone = milestone_project_id(project_id)

    return render(request, "tasks/tasks.html", {
        "current_task": current_task,
        "past_task": past_task,
        "future_task": future_task,
        "milestone": milestone,
        "date_today": date_today})


def open_tasks(request, project_id):
    user = request.user
    if user.is_authenticated():
        tasks = project_open_tasks(project_id)
        project = Projects.objects.get(id=project_id)

        date_today = datetime.datetime.now().date()

        return render(request, "tasks/project_tasks.html", {
            "date_today": date_today,
            "current_task": tasks,
            "name": "Open Task {}".format(project.name)})
    else:
        return redirect("/")


def close_tasks(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        tasks = project_close_tasks(project_id)

        date_today = datetime.datetime.now().date()

        return render(request, "tasks/project_tasks.html", {
            "date_today": date_today,
            "current_task": tasks,
            "name": "Close Task {}".format(project.name)})
    else:
        return redirect("/")


def open_milestone(request, project_id):
    user = request.user
    if user.is_authenticated():
        tasks = project_open_milestone(project_id)
        project = Projects.objects.get(id=project_id)

        date_today = datetime.datetime.now().date()

        return render(request, "tasks/project_milestone.html", {
            "date_today": date_today,
            "milestone": tasks,
            "name": "Open Milestone {}".format(project.name)})
    else:
        return redirect("/")


def close_milestone(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        tasks = project_close_milestone(project_id)

        date_today = datetime.datetime.now().date()

        return render(request, "tasks/project_milestone.html", {
            "date_today": date_today,
            "milestone": tasks,
            "name": "Close Milestone {}".format(project.name)})
    else:
        return redirect("/")


@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        user_name = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get('password')
        try:
            urs = User.objects.get(email=email)
            response = dict(message='fail')
        except Exception:
            User.objects.create_user(username=user_name,
                                     password=password)
            urs = User.objects.get(username=user_name)
            urs.email = email
            urs.save()
            response = dict(message='success')

        return HttpResponse(json.dumps(response))


@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        user_name = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=user_name, password=password)
        if user:
            login(request, user)
            response = dict(message='success')
        else:
            response = dict(message='fail')
        return HttpResponse(json.dumps(response))


def client_list(request):
    user = request.user
    if user.is_authenticated():
        hdfc_close = Projects.objects.filter(name__icontains='hdfc', status='closed', owner_name=user.username)
        hdfc_open = Projects.objects.filter(name__icontains='hdfc', status='active')
        indus_open = Projects.objects.filter(name__icontains='indusind', status='active')
        indus_closed = Projects.objects.filter(name__icontains='indusind', status='closed')
        hdfc_percent = len(hdfc_close) / len(hdfc_open) + len(hdfc_close) * 100
        indus_percent = len(indus_closed) / len(indus_open) + len(indus_closed) * 100

        project = [dict(name="HDFC BANK", search='hdfc', open=len(hdfc_open), closed=len(hdfc_close), percent=hdfc_percent),
                   dict(name="Indusind BANK", search='indusind', open=len(indus_open),
                        closed=len(indus_closed), percent=indus_percent)]

        return render(request, "clients.html", {
            "project": project})
    else:
        return redirect("/")


def resource_utilisation(request):
    user = request.user
    if user.is_authenticated():
        project = resource_utilisation_all()
        return HttpResponse(json.dumps(dict(users=project)))
        # return render(request, "project_list.html", {"projects": project})
    else:
        return redirect("/")


def project_list(request, name):
    user = request.user
    if user.is_authenticated():
        project = project_list_view(name)
        return render(request, "project_list.html", {"projects": project})
    else:
        return redirect("/")


def logout_user(request):
    logout(request)
    return redirect("/")


def projects_pull(request):
    code = request.GET.get("code", "")
    url = "https://accounts.zoho.com/oauth/v2/token"

    querystring = {
        "code": code,
        "redirect_uri": settings.REDIRECT_URL,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "grant_type": "authorization_code"}

    headers = {
        'cache-control': "no-cache",
        'postman-token': "4627606a-4fa6-897d-01c9-3f41002504e2"
    }

    response = requests.request("POST", url, headers=headers,
                                params=querystring)
    try:
        vals = response.json()
        vals['code'] = code
        access = Tokens.objects.latest("id")
        access.access_token = vals['access_token']
        access.created_at = datetime.datetime.now()
        access.code = code
        access.save()
        port = settings.PORTAL_ID

    except Exception:

        port = settings.PORTAL_ID

    if port:
        projects = all_projects()
        return redirect("/tasks_pull/")
    else:
        return HttpResponse(json.dumps(dict(error="Auth error")))


def tasks_pull(request):
    code = request.GET.get("code", "")
    url = "https://accounts.zoho.com/oauth/v2/token"

    querystring = {
        "code": code,
        "redirect_uri": settings.REDIRECT_URL,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "grant_type": "authorization_code"}

    headers = {
        'cache-control': "no-cache",
        'postman-token': "4627606a-4fa6-897d-01c9-3f41002504e2"
    }

    response = requests.request("POST", url, headers=headers,
                                params=querystring)
    try:
        vals = response.json()
        vals['code'] = code
        access = Tokens.objects.latest("id")
        access.access_token = vals['access_token']
        access.created_at = datetime.datetime.now()
        access.code = code
        access.save()
        port = settings.PORTAL_ID

    except Exception:

        port = settings.PORTAL_ID

    if port:
        tasks = all_projects_task()
        return redirect("/time_sheet_pull/")
    else:
        return HttpResponse(json.dumps(dict(error="Auth error")))


def milestone_pull(request):
    code = request.GET.get("code", "")
    url = "https://accounts.zoho.com/oauth/v2/token"

    querystring = {
        "code": code,
        "redirect_uri": settings.REDIRECT_URL,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "grant_type": "authorization_code"}

    headers = {
        'cache-control': "no-cache",
        'postman-token': "4627606a-4fa6-897d-01c9-3f41002504e2"
    }

    response = requests.request("POST", url, headers=headers,
                                params=querystring)
    try:
        vals = response.json()
        vals['code'] = code
        access = Tokens.objects.latest("id")
        access.access_token = vals['access_token']
        access.created_at = datetime.datetime.now()
        access.code = code
        access.save()
        port = settings.PORTAL_ID

    except Exception:

        port = settings.PORTAL_ID

    if port:
        milestone = all_projects_milestone()
        return redirect("/projects/")
    else:
        return HttpResponse(json.dumps(dict(error="Auth error")))


def projects_grant(request):
    return render(request, "projects_grantt.html")


def time_sheet_pull(request):
    code = request.GET.get("code", "")
    url = "https://accounts.zoho.com/oauth/v2/token"

    querystring = {
        "code": code,
        "redirect_uri": settings.REDIRECT_URL,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "grant_type": "authorization_code"}

    headers = {
        'cache-control': "no-cache",
        'postman-token': "4627606a-4fa6-897d-01c9-3f41002504e2"
    }

    response = requests.request("POST", url, headers=headers,
                                params=querystring)
    try:
        vals = response.json()
        vals['code'] = code
        access = Tokens.objects.latest("id")
        access.access_token = vals['access_token']
        access.created_at = datetime.datetime.now()
        access.code = code
        access.save()
        port = settings.PORTAL_ID

    except Exception:

        port = settings.PORTAL_ID

    if port:
        timesheet = all_project_time_sheet()
        return redirect("/milestone_pull/")
    else:
        return HttpResponse(json.dumps(dict(error="Auth error")))


def resource_utilization(request):
    today = datetime.datetime.now()
    days = today.weekday()
    week_start = today - datetime.timedelta(days=days)
    week_end = today + datetime.timedelta(days=days)
    print week_end
    time_users = TimeSheet.objects.all().values_list("owner_name")
    user_set = [str(user[0]) for user in set(time_users)]
    week_days = []
    for d in range(5):
        if d == 0:
            days = datetime.datetime.strftime(week_start, "%b %d")
        elif days == 5:
            days = datetime.datetime.strftime(week_end, "%b %d")
        else:
            date = week_start + datetime.timedelta(days=d)
            days = datetime.datetime.strftime(date, "%b %d")
        week_days.append(dict(week_date=days))
    response = []
    week_end = week_end + datetime.timedelta(days=1)
    for u in user_set:
        time_sheet_week = TimeSheet.objects.filter(last_modified_date__gte=week_start, last_modified_date__lte=week_end, owner_name=u)
        time_sheet = []
        for d in range(5):
            time_sheet_data = TimeSheet.objects.filter(
                last_modified_date=week_start + datetime.timedelta(days=d),
                owner_name=u).values_list("total_minutes")
            time_sheet.append(sum([int(f[0]) for f in time_sheet_data])/60)

        user = u
        week_hours = sum([int(d.hours) for d in time_sheet_week])
        response.append(dict(user=user,
                             week_hours=week_hours,
                             days_log=time_sheet
                             ))

    return render(request, 'resource.html',
                  {
                      "week": datetime.datetime.strftime(week_start, "%b %d") + " - " + datetime.datetime.strftime(week_end, "%b %d"),
                      "week_days":week_days,
                      "response": response
                  })

def home(request):
    return render(request, "home.html")

