# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
import pytz
from django.views.decorators.csrf import csrf_exempt
from projects import *
from tasks import *
from milestone import *
from time_sheet import *
from django.contrib.auth.models import User
from task_list import all_project_task_list
from task_wise_list import *

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
    user = request.user
    if user.is_authenticated:
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
            access = Tokens.objects.get(user=user)
            access.access_token = vals['access_token']
            access.created_at = datetime.datetime.now()
            access.code = code

            access.save()
            port = settings.PORTAL_ID

        except Exception:
            vals = response.json()
            vals['code'] = code
            access = Tokens.objects.create(user=user)
            access.access_token = vals['access_token']
            access.created_at = datetime.datetime.now()
            access.code = code

            access.save()
            port = settings.PORTAL_ID

        if port:

            return render(request, "zohouser/intermediate.html")
    else:
        return redirect("/")


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
        # try:
        csms = request.GET.get("csm")
        if csms == "all":
            project = user.projects_set.all().order_by("name")
        elif csms == None:
            project = user.projects_set.all().order_by("name")
        else:
            project = Projects.objects.filter(owner_name=csms).order_by(
                "name")


        response = []
        pname = []
        csm_list = []
        csm_data = Projects.objects.all().values_list("owner_name")
        for c in csm_data:
            name = str(c[0])
            if name not in csm_data:
                csm_list.append(name)
        # csm = list(set([str(u[0]) for u in csm_data]))
        sorted(list(set(csm_list)))

        for p in project:
            open_task = p.tasks_set.filter(status='Open').count()
            progress_task = p.tasks_set.filter(status='In Progress').count()
            closed_task = p.tasks_set.filter(status='Closed').count()
            open_milestone = p.milestone_set.filter(status='notcompleted').count()
            closed_milestone = p.milestone_set.filter(status='completed').count()
            try:
                datetime.datetime.strftime(p.end_date_format, "%Y-%m-%d")
                if p.end_date_format < datetime.datetime.now().date() and p.status.lower() == "active":
                    status = 'red'
                else:
                    status = "green"
            except Exception:
                status = 'red'
            try:
                health = closed_task / (open_task + closed_task + progress_task)
            except Exception:
                health = 0
            if p.name not in pname:
                pname.append(p.name)
                response.append(dict(
                    name=p.name,
                    owner=p.owner_name,
                    open_task=open_task,
                    progress_task=progress_task + open_task + closed_task,
                    closed_task=closed_task,
                    status=p.status.capitalize(),
                    color=status,
                    closed_milestone=closed_milestone,
                    total_milestone=closed_milestone + open_milestone,
                    start_date=p.start_date_format,
                    end_date=p.end_date_format,
                    id=p.id,
                    percent=round(health * 100)
                ))
        return render(request, "zohouser/projects.html", {"project": response,
                                                 "csm": list(set(csm_list))})
    except Exception:
        return redirect("/")


def projects_grantt(request):
    user = request.user
    try:
        # user = User.objects.get(username=user.username)
        if "hdfc" in user.username:

            project = Projects.objects.filter(name__icontains='hdfc', start_date_format__year__gte=
                                               datetime.datetime.now().year - 1).order_by(
                "name")
        elif "indusind" in user.username:


            project = Projects.objects.filter(name__icontains='indusind',
                                              start_date_format__year__gte=
                                              datetime.datetime.now().year - 1).order_by(
                "name")
        else:

            project = user.projects_set.filter(start_date_format__year__gte=
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
                                     percent=round(percent * 100, 2),
                                     tasks=task_data))
        return HttpResponse(json.dumps(dict(data=response)))
    except Exception:
        return redirect("/")


def project_detail(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = project_detail_view(project_id)
        return render(request, "zohouser/project_detail.html", {"project": project})
    else:
        return redirect("/")


def time_sheet_task(request, task_id):
    user = request.user
    if user.is_authenticated():
        tasks,task_name = time_sheet_projects(task_id)
        return render(request, "zohouser/time_sheet.html", dict(tasks=tasks,
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
        response = []
        for m in milestone:
            tasks = Tasks.objects.filter(milestone_id=m.id_string)
            user = ""
            for t in tasks:
                user_list = t.zohousers_set.all()
                user = ",".join(list(set([u.username for u in user_list])))
            response.append(dict(
                project=project.name,
                owner_name=m.owner_name,
                name=m.name,
                status=m.status,
                start_date=m.start_date,
                end_date=m.end_date,
                sequence=m.sequence,
                flag=m.flag,
                users=user
            ))
        current_task,past_task,future_task = project_task_list(project_id)
        date_today = datetime.datetime.now().date()

        return render(request, "zohouser/tasks.html", {
                                            "current_task": current_task,
                                            "past_task": past_task,
                                            "future_task": future_task,
                                            "milestone":response,
                                             "date_today": date_today,
                                            "name": project.name})
    else:
        return redirect("/")


def milestone_data(request, project_id):
    user = request.user
    if user.is_authenticated():
        mile_stone = milestone_project_id(project_id)
        return render(request, "zohouser/mile_stone.html", dict(mile_stone=mile_stone))
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

    return render(request, "zohouser/tasks/tasks.html", {
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

        return render(request, "zohouser/tasks/project_tasks.html", {
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

        return render(request, "zohouser/tasks/project_tasks.html", {
            "date_today": date_today,
            "current_task": tasks,
            "name": "Close Task {}".format(project.name)})
    else:
        return redirect("/")


def all_tasks(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        tasks = project_all_tasks(project_id)
        tasks.sort(key=lambda hotel: hotel['status'], reverse=True)
        date_today = datetime.datetime.now().date()

        return render(request, "zohouser/tasks/project_tasks.html", {
            "date_today": date_today,
            "current_task": tasks,
            "name": "ALL Task {}".format(project.name)})
    else:
        return redirect("/")


def open_milestone(request, project_id):
    user = request.user
    if user.is_authenticated():
        tasks = project_open_milestone(project_id)
        project = Projects.objects.get(id=project_id)

        date_today = datetime.datetime.now().date()

        return render(request, "zohouser/tasks/project_milestone.html", {
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

        return render(request, "zohouser/tasks/project_milestone.html", {
            "date_today": date_today,
            "milestone": tasks,
            "name": "Close Milestone {}".format(project.name)})
    else:
        return redirect("/")


def all_milestone(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        tasks = project_all_milestone(project_id)
        tasks.sort(key=lambda hotel: hotel['status'], reverse=True)

        date_today = datetime.datetime.now().date()

        return render(request, "zohouser/tasks/project_milestone.html", {
            "date_today": date_today,
            "milestone": tasks,
            "name": project.name})
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
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = User.objects.get(email=email)
        except Exception:
            user = User.objects.create(email=email, username=email)
            use = User.objects.get(email=email)
            use.set_password(password)
            use.save()

        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            if "indigo" in email:
                response = dict(message='success', redirect='auth')
            else:
                response = dict(message='success', redirect='client')
        else:
            response = dict(message='fail')
        return HttpResponse(json.dumps(response))


def client_list(request):
    user = request.user
    if user.is_authenticated():
        if "hdfc" in user.username:
            hdfc_close = Projects.objects.filter(name__icontains='hdfc', status__in=['closed', "Closed",])
            hdfc_open = Projects.objects.filter(name__icontains='hdfc', status__in=['active', 'Active'])
            hdfc_percent = len(hdfc_close) / (len(hdfc_open) + len(hdfc_close))
            hper = hdfc_percent * 100

            hdfc_query_red = Q(name__icontains='hdfc',
                               status__in=['active', 'Active'],
                               end_date_format__lte=datetime.datetime.now().date()) | Q(
                name__icontains='hdfc',
                status__in=['active', 'Active', 'closed', "Closed"],
                end_date_format=None)
            hdfc_query_green = Q(name__icontains='hdfc',
                                 status__in=['closed', "Closed", 'active',
                                             'Active'],
                                 end_date_format__gte=datetime.datetime.now().date()) or \
                               Q(name__icontains='indusind',
                                 status__in=['closed', "Closed"],
                                 )
            red_hdfc = Projects.objects.filter(hdfc_query_red).count()
            green_hdfc = Projects.objects.filter(hdfc_query_green).exclude(
                end_date_format=None).count()
            project = [
                dict(name="HDFC BANK", search='hdfc', open=len(hdfc_open),
                     closed=len(hdfc_close), percent=round(hper, 2),
                     red=red_hdfc, green=green_hdfc),

                ]
        elif "indusind" in user.username:
            indus_open = Projects.objects.filter(name__icontains='indusind', status='active')
            indus_closed = Projects.objects.filter(name__icontains='indusind', status='closed')
            try:
                indus_percent = len(indus_closed) / (len(indus_open) + len(indus_closed))
            except Exception:
                indus_percent = 0
            indu = indus_percent * 100
            indusind_query_red = Q(name__icontains='indusind',
                               status__in=['active', 'Active'],
                               end_date_format__lte=datetime.datetime.now().date()) | Q(
                name__icontains='indusind',
                status__in=['active', 'Active', 'closed', "Closed"],
                end_date_format=None)
            indusind_query_green = Q(name__icontains='indusind',
                                 status__in=['closed', "Closed", 'active',
                                             'Active'],
                                 end_date_format__gte=datetime.datetime.now().date()) or \
                                   Q(name__icontains='indusind',
                                 status__in=['closed', "Closed", 'active',
                                             'Active'],
                                 end_date_format__gte=datetime.datetime.now().date())

            red_indusind = Projects.objects.filter(indusind_query_red).count()
            green_indusind = Projects.objects.filter(indusind_query_green).exclude(
                end_date_format=None).count()
            project = [
                dict(name="Indusind BANK", search='indusind',
                     open=len(indus_open),
                     closed=len(indus_closed), percent=round(indu, 2),
                     red=red_indusind, green=green_indusind),
                ]
        else:
            project = []

        return render(request, "zohouser/clients.html", {
            "project": project})
    else:
        return redirect("/")


def client_tasks(request, name):
    if name == "all":
        task_open = Tasks.objects.filter(status__in=['open', 'Open']).count()
        task_inprogress = Tasks.objects.filter(status__in=['in progress',
                                                           'In Progress']).count()
        task_closed = Tasks.objects.filter(status__in=['open', 'Open']).count()
    else:
        task_open = Tasks.objects.filter(project__name__icontains=name,
                                         status__in=['open', 'Open']).count()
        task_inprogress = Tasks.objects.filter(project__name__icontains=name,
                                               status__in=['in progress',
                                                           'In Progress']).count()
        task_closed = Tasks.objects.filter(project__name__icontains=name,
                                           status__in=['open', 'Open']).count()

    return HttpResponse(json.dumps(dict(task_open=task_open, task_inprogress=task_inprogress,task_closed=task_closed)))


def project_list(request):
    user = request.user
    if user.is_authenticated():
        today = datetime.datetime.now().date()
        name = request.GET.get('name')
        status = request.GET.get('status')
        csms = request.GET.get('csm')
        color = request.GET.get('color')
        csm_data = Projects.objects.all().values_list("owner_name")
        csm_list = []
        first,last=get_month_day_range(today)
        for c in csm_data:
            names = str(c[0])
            if names not in csm_data:
                csm_list.append(names)
        if color:
            project = project_list_view_color(name, csms, color)
        else:
            project = project_list_view(name, status, csms)
        sorted(list(set(csm_list)))
        total_projects = len(project)
        if name == "hdfc":
            active = Projects.objects.filter(name__icontains=name, status__in=['active', 'Active'], end_date_format__range=[first, last]).count()
            closed = Projects.objects.filter(name__icontains=name, status__in=['Closed', 'closed'], end_date_format__range=[first, last]).count()
            task_open = Tasks.objects.filter(project__name__icontains=name,
                                             status__in=['open',
                                                         'Open']).count()
            task_inprogress = Tasks.objects.filter(
                project__name__icontains=name,
                status__in=['in progress',
                            'In Progress']).count()
            task_closed = Tasks.objects.filter(project__name__icontains=name,
                                               status__in=['closed',
                                                           'Closed']).count()
            date_today = datetime.datetime.now().date()
            week_day = date_today.weekday()
            begin_date = datetime.datetime.now().date() - datetime.timedelta(
                days=week_day)
            end_date = datetime.datetime.now().date() + datetime.timedelta(
                days=6 - week_day)
            this_week = Tasks.objects.filter(project__name__icontains=name, end_date__gte=begin_date, end_date__lte=end_date).count()

        else:
            active = Projects.objects.filter(status__in=['active', 'Active'],
                                             end_date_format__range=[first,
                                                                     last]).count()
            closed = Projects.objects.filter(status__in=['Closed', 'closed'],
                                             end_date_format__range=[first,
                                                                     last]).count()
            task_open = Tasks.objects.filter(status__in=['open',
                                                         'Open']).count()
            task_inprogress = Tasks.objects.filter(status__in=['in progress',
                            'In Progress']).count()
            task_closed = Tasks.objects.filter(status__in=['Closed',
                                                           'closed']).count()
            date_today = datetime.datetime.now().date()
            week_day = date_today.weekday()
            begin_date = datetime.datetime.now().date() - datetime.timedelta(
                days=week_day)
            end_date = datetime.datetime.now().date() + datetime.timedelta(
                days=6 - week_day)
            this_week = Tasks.objects.filter(end_date__gte=begin_date,
                                             end_date__lte=end_date).count()
        month = datetime.datetime.strftime(today, "%B")

        return render(request, "zohouser/project_list_pie.html",
                          {"projects": project,
                           "csm": list(set(csm_list)),
                           "date": today,
                           "name": name,
                           "status": status,
                           "user_name": user.email,
                           "total_projects": total_projects,
                           "active": active,
                           "closed": closed,
                           "task_closed": task_closed,
                           "task_open": task_open,
                           "task_inprogress": task_inprogress,
                           "this_week": this_week,
                           "month": month
                           })
            # return render(request, "zohouser/project_list.html",
            #               {"projects": project,
            #                "csm": list(set(csm_list)),
            #                "date": today,
            #                "name": name,
            #                "status": status,
            #                "user_name": user.email,
            #                "total_projects": total_projects,
            #                "active": active,
            #                "closed": closed,
            #
            #
            #                })


    else:
        return redirect("/")


def logout_user(request):
    logout(request)
    return redirect("/")


def projects_pull(request):
    user = request.user
    if user.is_authenticated:
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
            projects = all_projects(user)
            # return redirect("/tasks_pull/")
        return HttpResponse("Success")
    else:
        return redirect("/")


def tasks_list_pull(request):
    user = request.user
    if user.is_authenticated:
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
            tasks = all_project_task_list(user)
            return HttpResponse("success")
            # return redirect("/time_sheet_pull/")
    else:
        return redirect("/")


def tasks_pull(request):
    user = request.user
    if user.is_authenticated:
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
            tasks = all_projects_task(user)
            return HttpResponse("success")
            # return redirect("/time_sheet_pull/")
    else:
        return redirect("/")


def sub_tasks_pull(request):
    user = request.user
    if user.is_authenticated:
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
            tasks = user.tasks_set.all()
            for t in tasks:
                pull_subtasks(t, user)
            return HttpResponse("success")
            # return redirect("/time_sheet_pull/")
    else:
        return redirect("/")


def milestone_pull(request):
    user = request.user
    if user.is_authenticated:
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
            milestone = all_projects_milestone(user=user,)
            return HttpResponse("success")
    else:
        return HttpResponse(json.dumps(dict(error="Auth error")))


def projects_grant(request):
    user = request.user
    if user.is_authenticated():
        return render(request, "zohouser/projects_grantt.html")
    else:
        return redirect("/")


def time_sheet_pull(request):
    user = request.user
    if user.is_authenticated:
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
            timesheet = all_project_time_sheet(user=user,)
            return HttpResponse("success")
    else:
        return HttpResponse(json.dumps(dict(error="Auth error")))


def is_leap_year(year):
    return (year % 4 == 0) and (year % 100 != 0) or (year % 400 == 0)


def resource_utilization(request):
    user = request.user
    if user.is_authenticated():
        today = datetime.datetime.now()
        days_left = today.weekday()
        year = today.year
        month = today.month
        if month in [4, 6, 9, 11]:
            end_days = 30
        elif month in [1, 3, 5, 7, 8, 10, 12]:
            end_days = 31
        elif month == 2 and is_leap_year(year) == True:
            end_days = 29
        elif month == 2 and is_leap_year(year) == False:
            end_days = 28
        else:
            end_days = 0
        days = today.day
        month_end = today + datetime.timedelta(days=days)
        month_start = today - datetime.timedelta(days=days - 1)

        week_start = today - datetime.timedelta(days=days_left)
        week_end = today + datetime.timedelta(days=5 - days_left)
        time_users = user.timesheet_set.all().values_list("owner_name")
        user_set = [str(user[0]) for user in set(time_users)]
        week_days = []
        for d in range(5):
            if d == 0:
                days = datetime.datetime.strftime(week_start, "%b %d")
            elif d == 5:
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
            for d in range(5):
                time_sheet_data = TimeSheet.objects.filter(
                    last_modified_date=(week_start + datetime.timedelta(days=d)).date(),
                    owner_name=u).values_list("total_minutes")
                time_sheet.append(float(sum([int(f[0]) for f in time_sheet_data])/ 60))

            user = u
            week_hours = float(sum([int(d.total_minutes) for d in time_sheet_week]) / 60)
            month_logs = float(sum([int(d.total_minutes) for d in time_sheet_month]) / 60)

            response.append(dict(user=" ".join(user.split(".")).upper(),
                                 week_hours=week_hours,
                                 days_log=time_sheet,
                                 user_name=user,
                                 month=month_logs
                                 ))
        from operator import itemgetter

        response = sorted(response, key=itemgetter('user'))

        return render(request, 'zohouser/resource.html',
                      {
                          "week": datetime.datetime.strftime(week_start, "%b %d") + " - " + datetime.datetime.strftime(week_end, "%b %d"),
                          "week_days":week_days,
                          "response": response
                      })
    else:
        return redirect("/")


def time_sheet_range(request):
    tasks = Tasks.objects.all()
    for p in tasks:
        if p.timesheet_url == "" or p.timesheet_url == None:
            pass
        else:
            url = p.timesheet_url
            task_time_sheet(url=url, task=p)
    return HttpResponse("test")


def task_list_projects(request, project_id):
    user = request.user
    today = datetime.datetime.now().date()
    if user.is_authenticated():
        # project = Projects.objects.get(id=project_id)
        # tasks = project.tasks_set.all()
        # response = []

        projects = project_data_parse(project_id)

        return render(request, "zohouser/sub_task_lists.html",
                  dict(project=projects,
                       total=len(projects),
                       today=today,
                       ))
        # data = task_list_project(project_id)

        # return render(request,"zohouser/sub_task_lists.html", dict(tasks=data, project=project.name))
    else:
        return redirect("/")


def project_task_time_sheet(request, task_id):
    user = request.user
    if user.is_authenticated():
        task = Tasks.objects.get(id=task_id)
        return render(request, "zohouser/time_sheet.html", {"tasks": task.timesheet_set.all(),
                                               "task_name": task.project.name + " - " + task.task_name, })
    else:
        return redirect("/")


def task_bifurcate(request, project_id):
    user = request.user
    if user.is_authenticated():
        task_sep = request.GET.get("task")
        project = Projects.objects.get(id=project_id)
        current_task, future_date_one_week, past_date_one_week, past_date_two_week = project_task_list_week(project_id)
        if task_sep == "past_two":
            task = past_date_two_week
        elif task_sep == "past_one":
            task = past_date_one_week
        elif task_sep == "present":
            task = current_task
        else:
            task = future_date_one_week
        response = []
        for t in task:
            try:
                start_date = datetime.datetime.strftime(t.start_date, "%b, %d %Y")
            except Exception:
                start_date = None
            try:
                end_date = datetime.datetime.strftime(t.end_date, "%b, %d %Y")
            except Exception:
                end_date = None
            response.append(dict(
                task_name=t.task_name,
                start_date=start_date,
                end_date=end_date,
                status=t.status,
                time_sheet=len(t.timesheet_set.all()),
            ))
        return render(request,"zohouser/task_lists.html", dict(tasks=response, project=project.name))
    return redirect("/")


def sub_tasks(request, task_id):
    user = request.user
    if user.is_authenticated():
        sub_task = SubTasks.objects.filter(tasks__id=task_id)
        sub_tasks = []
        for s in sub_task:
            task = s.tasks.task_name
            # time_sheet = s.tasks.timesheet_set.all()
            users = ",".join(list(set([u.owner_name for u in s.tasks.timesheet_set.all()])))
            sub_tasks.append(dict(
                task_name=task,
                sub_task=s.name,
                start_date=s.start_date,
                end_date=s.end_date,
                users=users,
                completed=s.completed,
                percent_complete=s.percent_complete,
                status=s.completed,
                owner=s.created_person,
            ))
        return render(request, "zohouser/tasks/sub_tasks.html",{"current_task": sub_tasks})
    else:
        return redirect("/")


def mile_stone_tasks(request, milestone):
    user = request.user
    if user.is_authenticated():
        mile = Milestone.objects.get(id=milestone)
        project = mile.project
        user = ""
        task = Tasks.objects.filter(milestone_id=mile.id_string)
        response = []
        for t in task:
            user_list = t.zohousers_set.all()
            user = ",".join(list(set([u.username for u in user_list])))
            response.append(dict(
                project=project.name,
                owner_name=mile.owner_name,
                name=mile.name,
                status=mile.status,
                start_date=mile.start_date,
                end_date=mile.end_date,
                sequence=mile.sequence,
                flag=mile.flag,
                users=user
            ))
        return render(request, "zohouser/tasks/project_tasks.html", {"current_task": task})
    else:
        return redirect("/")


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


def project_filter(request):
    user = request.user
    if user.is_authenticated():

        csm_list = []
        csm = request.GET.get("csm", "all")
        project_name = request.GET.get("project_name", "all")
        if "indigo" in user.email:
            if project_name == "all":
                projects = parse_project_data(csm,user)
            else:
                projects = parse_project_data_project(project_name)
            csm_data = Projects.objects.all().values_list("owner_name")
        else:
            if project_name == "all":
                projects = parse_project_data(csm, user)
            else:
                projects = parse_project_data_project(project_name)
            csm_data = Projects.objects.filter(name__icontains="hdfc").values_list("owner_name")

        for c in csm_data:
            names = str(c[0])
            if names not in csm_data:
                csm_list.append(names)
        csm_list = list(set(csm_list))
        today = datetime.datetime.now()
        return render(request, "zohouser/filter.html",
                  dict(projects=projects,
                       csm=csm_list,
                       total=len(projects),
                       today=today,
                       name=csm
                       ))
    else:
        return redirect("/")


def intermediate(request):
    user = request.user
    if user.is_authenticated():
        return render(request, "zohouser/intermediate.html")
    else:
        return redirect("/")


def task_weekly(request):
    user = request.user
    if user.is_authenticated():
        name = request.GET.get("name")
        date_today = datetime.datetime.now().date()
        week_day = date_today.weekday()
        begin_date = datetime.datetime.now().date() - datetime.timedelta(
            days=week_day)
        end_date = datetime.datetime.now().date() + datetime.timedelta(
            days=6 - week_day)
        if name == "all":
            this_week = Tasks.objects.filter(end_date__gte=begin_date,
                                             end_date__lte=end_date)
        else:
            this_week = Tasks.objects.filter(project__name__icontains=name,
                                         end_date__gte=begin_date,
                                         end_date__lte=end_date)
        return render(request, "zohouser/tasks/project_tasks.html",{
            "current_task": this_week
        })
    else:
        return redirect("/")


def project_list_color(request):
    user = request.user
    if user.is_authenticated():
        today = datetime.datetime.now().date()
        color = request.GET.get('color')
        if "hdfc" in user.email:
            csm_data = Projects.objects.filter(name__icontains="hdfc").values_list("owner_name")
        else:
            csm_data = Projects.objects.all().values_list("owner_name")

        csm_list = []
        for c in csm_data:
            names = str(c[0])
            if names not in csm_data:
                csm_list.append(names)
        project = parse_project_data_color(user)
        sorted(list(set(csm_list)))
        total_projects = len(project)
        red_project = []
        yellow_project = []
        green_project = []
        for pro in project:
            percent = pro['color']
            if percent == "green":
                green_project.append(pro)
            elif percent == "red":
                red_project.append(pro)
            else:
                yellow_project.append(pro)
        # color = color.split(",")
        if color == "red":
            return render(request, "zohouser/filter_new_red.html",
                      {"projects": red_project,
                       "csm": list(set(csm_list)),
                       "date": today,
                       "user_name": user.email,
                       "total_projects": total_projects,
                       "color": color

                       })
        elif color == "yellow":
            return render(request, "zohouser/filter_new_orange.html",
                          {"projects": yellow_project,
                           "csm": list(set(csm_list)),
                           "date": today,
                           "user_name": user.email,
                           "total_projects": total_projects,
                           "color": color

                           })
        elif color == "green":
            return render(request, "zohouser/filter_new_green.html",
                          {"projects": yellow_project,
                           "csm": list(set(csm_list)),
                           "date": today,
                           "user_name": user.email,
                           "total_projects": total_projects,
                           "color": color

                           })
        elif color == "red,green":

            return render(request, "zohouser/filter_new_red_green.html",
                          {"projects": red_project + green_project,
                           "csm": list(set(csm_list)),
                           "date": today,
                           "user_name": user.email,
                           "total_projects": total_projects,
                           "color": color

                           })
        elif color == "red,yellow":

            return render(request, "zohouser/filter_new_red_yellow.html",
                          {"projects": red_project + yellow_project,
                           "csm": list(set(csm_list)),
                           "date": today,
                           "user_name": user.email,
                           "total_projects": total_projects,
                           "color": color

                           })
        elif color == "yellow,green":
            print 1
            return render(request, "zohouser/filter_new_yellow_green.html",
                          {"projects": yellow_project + green_project,
                           "csm": list(set(csm_list)),
                           "date": today,
                           "user_name": user.email,
                           "total_projects": total_projects,
                           "color": color

                           })

        else:
            return render(request, "zohouser/filter_new.html",
                      {"projects": red_project + yellow_project + green_project,
                       "csm": list(set(csm_list)),
                       "date": today,
                       "user_name": user.email,
                       "total_projects": total_projects,
                       "color": color

                       })

    else:
        return redirect("/")


# def csm_data(request):
#     user =request.user
#     if user.is_authenticated():
#         csm_data = Projects.objects.all().values_list("owner_name")
#         csm_list = []
#         for c in csm_data:
#             names = str(c[0])
#             if names not in csm_data:
#                 csm_list.append(names)
#         response = []
#         for c in csm_list:
#             project_closed = Projects.objects.filter(owner_name=c, status__in=['closed', 'Closed'])
#             project_open = Projects.objects.filter(owner_name=c, status__in=['Active', 'active'])
#
#     else:
#         return redirect("/")


def project_ux(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        ux_task = task_ux(project)
        ux_task = task_filter_all(ux_task)
        ux_task.sort(key=lambda hotel: hotel['status'], reverse=True)
        return render(request, "zohouser/task_wise_list.html", {"tasks":ux_task,"task_type": "UX"})
    else:
        return redirect("/")


def project_ui(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        ux_task = task_ui(project)
        ux_task = task_filter_all(ux_task)
        ux_task.sort(key=lambda hotel: hotel['status'], reverse=True)
        return render(request, "zohouser/task_wise_list.html", {"tasks":ux_task,
                                                                "task_type": "UI"})
    else:
        return redirect("/")


def project_html(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        ux_task = task_html(project)
        ux_task = task_filter_all(ux_task)
        ux_task.sort(key=lambda hotel: hotel['status'], reverse=True)
        return render(request, "zohouser/task_wise_list.html", {"tasks":ux_task,
                                                                "task_type": "HTML"})
    else:
        return redirect("/")


def project_api(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        ux_task = task_api(project)
        ux_task = task_filter_all(ux_task)
        ux_task.sort(key=lambda hotel: hotel['status'], reverse=True)
        return render(request, "zohouser/task_wise_list.html", {"tasks":ux_task,
                                                                "task_type": "API"})
    else:
        return redirect("/")


def project_bee(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        ux_task = task_bee(project)
        ux_task = task_filter_all(ux_task)
        ux_task.sort(key=lambda hotel: hotel['status'], reverse=True)
        return render(request, "zohouser/task_wise_list.html", {"tasks":ux_task,
                                                                "task_type": "BEE"})
    else:
        return redirect("/")


def project_qc(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        ux_task = task_qc(project)
        ux_task = task_filter_all(ux_task)
        ux_task.sort(key=lambda hotel: hotel['status'], reverse=True)
        return render(request, "zohouser/task_wise_list.html", {"tasks":ux_task,
                                                                "task_type": "QC"})
    else:
        return redirect("/")


def project_uat(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        ux_task = task_uat(project)
        ux_task = task_filter_all(ux_task)
        ux_task.sort(key=lambda hotel: hotel['status'], reverse=True)
        return render(request, "zohouser/task_wise_list.html", {"tasks":ux_task,
                                                                "task_type": "UAT"})
    else:
        return redirect("/")


def over_due_task(request):
    user = request.user
    name = request.GET.get("project_name")
    if user.is_authenticated():
        if name == "all":
            tasks = Tasks.objects.filter(status__in=['open',
                                                         'Open'])
        else:
            tasks = Tasks.objects.filter(project__name__icontains=name,
                                         status__in=['open',
                                                         'Open'])
        tasks = task_filter_all(tasks)
        tasks.sort(key=lambda hotel: hotel['created_time'], reverse=True)
        date_today = datetime.datetime.now().date()

        return render(request, "zohouser/task_wise_list.html", {
            "date_today": date_today,
            "tasks": tasks,
            "name": "Open Task All"})
    else:
        return redirect("/")


def pending_task(request):
    user = request.user
    name = request.GET.get("project_name")
    if user.is_authenticated():
        if name == 'all':
            tasks = Tasks.objects.filter(
                status__in=['in progress',
                            'In Progress'])
        else:
            tasks = Tasks.objects.filter(
                project__name__icontains=name,
                status__in=['in progress',
                            'In Progress'])
        tasks = task_filter_all(tasks)
        tasks.sort(key=lambda hotel: hotel['created_time'], reverse=True)

        date_today = datetime.datetime.now().date()

        return render(request, "zohouser/task_wise_list.html", {
            "date_today": date_today,
            "tasks": tasks,
            "name": "Pending Task All"})
    else:
        return redirect("/")


def closed_tasks(request):
    user = request.user
    name = request.GET.get("project_name")

    if user.is_authenticated():
        if name == 'all':
            tasks = Tasks.objects.filter(status__in=['closed',
                                                       'Closed'])
        else:
            tasks = Tasks.objects.filter(project__name__icontains=name,
                                               status__in=['closed',
                                                           'Closed'])
        tasks = task_filter_all(tasks)
        date_today = datetime.datetime.now().date()
        tasks.sort(key=lambda hotel: hotel['created_time'], reverse=True)

        return render(request, "zohouser/task_wise_list.html", {
            "date_today": date_today,
            "tasks": tasks,
            "name": "Close Task All"})
    else:
        return redirect("/")


def task_filter_all(tasks):
    response = []
    for t in tasks:
        description = strip_tags(t.description)
        user_list = t.zohousers_set.all()
        user = ",".join(list(set([u.username for u in user_list])))
        response.append(dict(
            project=t.project.name,
            owner_name=t.created_person,
            name=t.task_name,
            status=t.status,
            start_date=t.start_date,
            end_date=t.end_date,
            users=user,
            description=description[:50] + "..." if len(strip_tags(t.description)) > 50 else description,
            subtasks=t.subtasks,
            created_time=t.created_time,
            completed=t.completed,
            percent_complete=t.percent_complete,

        ))
    return response


def home(request):
    user = request.user
    if "hdfc" in user.username:
        return redirect("/project_list/?csm=all&name=hdfc&status=all")
    elif "indusind" in user.username:
        return redirect("/project_list/?csm=all&name=indusind&status=all")
    elif "indigo" in user.username:
        return redirect("/project_list/?csm=all&name=all&status=all")
    else:
        return render(request, "zohouser/home.html")
    # return redirect("/")


