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
            "name": "Open Task {}".format(project.name),
            "proj_id": project.id
            })
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
            "name": "Close Task {}".format(project.name),
            "proj_id": project.id
        })
    else:
        return redirect("/")


def all_tasks(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        tasks_data = project_all_tasks(project_id)
        tasks_data.sort(key=lambda hotel: hotel['status'], reverse=True)
        date_today = datetime.datetime.now().date()
        tasks = project.tasks_set.all()
        tasks_active = project.tasks_set.filter(status__in=['Open','open', 'in progress', 'In Progress']).count()
        tasks_closed = project.tasks_set.filter(status__in=['closed', 'Closed']).count()
        # task_over = project.tasks_set.filter(status__in=['Open','open', 'in progress', 'In Progress'], end_date__lt=date_today).count()
        # task_progress = project.tasks_set.filter(status__in=['Open','open', 'in progress', 'In Progress'], end_date__gte=date_today).count()
        # task_close = project.tasks_set.filter(status__in=['closed', 'Closed']).count()
        today = datetime.datetime.now().date()
        red, yellow, green = 0,0,0
        for t in tasks:
            if t.status in ["Open", "In Progress", "open",
                            "in progress"] and t.end_date and t.end_date < today:
                red += 1
            elif t.status in ["Open", "In Progress",
                              "open"] and t.end_date == None:
                red += 1
            elif t.status in ["closed", 'Closed'] and t.end_date == None:
                green += 1
            elif t.status in ["Open", "In Progress", "open",
                              'in progress'] and t.end_date and t.end_date > today:
                yellow += 1
            else:
                green += 1
        week_day = date_today.weekday()
        begin_date = datetime.datetime.now().date() - datetime.timedelta(
            days=week_day)
        end_date = datetime.datetime.now().date() + datetime.timedelta(
            days=4 - week_day)
        this_week = project.tasks_set.filter(end_date__gte=begin_date,
                                         end_date__lte=end_date).count()

        return render(request, "zohouser/tasks/project_tasks_all.html", {
            "date_today": date_today,
            "current_task": tasks_data,
            "name": "ALL Task {}".format(project.name),
            "total_projects": tasks.count(),
            "active":tasks_active,
            "closed":tasks_closed,
            "task_open":red,
            "task_inprogress":yellow,
            "task_closed":green,
            "this_week":this_week,
            "proj_id": project.id
        })
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
        total_projects = len(tasks)
        date_today = datetime.datetime.now().date()
        mile_stone_active = project.milestone_set.filter(status='notcompleted').count()
        mile_stone_closed = project.milestone_set.filter(status='completed').count()
        week_day = date_today.weekday()
        begin_date = datetime.datetime.now().date() - datetime.timedelta(
            days=week_day)
        end_date = datetime.datetime.now().date() + datetime.timedelta(
            days=4 - week_day)
        week = project.milestone_set.filter(end_date__range=[begin_date, end_date]).count()
        over_due_ms = project.milestone_set.filter(end_date__lt=date_today, status='notcompleted').count()
        pending_ms = project.milestone_set.filter(end_date__gte=date_today, status='notcompleted').count()
        completed_ms = project.milestone_set.filter( status='completed').count()
        return render(request, "zohouser/tasks/project_milestone.html", {
            "date_today": date_today,
            "milestone": tasks,
            "name": project.name,
            "proj_id": project.id,
            "total_projects":total_projects,
            "active":mile_stone_active,
            "closed":mile_stone_closed,
            "this_week": week,
            "task_open":over_due_ms,
            "task_inprogress": pending_ms,
            "task_closed": completed_ms
        })
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
    today = datetime.datetime.now().date()
    first, last = get_month_day_range(today)
    if name == "all":
        task_open = Tasks.objects.filter(status__in=['open', 'Open', 'in progress','In Progress'], end_date__range=[first,today]).count()
        task_inprogress = Tasks.objects.filter(status__in=['in progress',
                                                           'In Progress'], end_date__range=[today,last]).count()
        task_closed = Tasks.objects.filter(status__in=['Closed', 'closed',"close", "close"], last_updated_time__range=[first, last]).count()
    else:
        task_open = Tasks.objects.filter(project__name__icontains=name,
                                         status__in=['open', 'Open', 'in progress','In Progress'], end_date__gte=first, end_date__lt=today).count()
        task_inprogress = Tasks.objects.filter(project__name__icontains=name,
                                               status__in=['in progress',
                                                           'In Progress'], end_date__range=[today,last]).count()
        task_closed = Tasks.objects.filter(project__name__icontains=name,
                                           status__in=['Closed', 'closed',"close", "close"], last_updated_time__range=[first, last]).count()

    return HttpResponse(json.dumps(dict(task_open=task_open, task_inprogress=task_inprogress,task_closed=task_closed)))


def project_list(request):
    user = request.user
    if user.is_authenticated():
        today = datetime.datetime.now().date()
        first,last=get_month_day_range(today)
        name = request.GET.get('name')
        status = request.GET.get('status')
        csms = request.GET.get('csm')
        color = request.GET.get('color')
        csm_data = Projects.objects.all().values_list("owner_name")
        csm_list = []
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
            closed = Projects.objects.filter(name__icontains=name, status__in=['Completed', 'completed'], end_date_format__range=[first, last]).count()
            date_today = datetime.datetime.now().date()
            week_day = date_today.weekday()
            begin_date = datetime.datetime.now().date() - datetime.timedelta(
                days=week_day)
            end_date = datetime.datetime.now().date() + datetime.timedelta(
                days=4 - week_day)
            this_week = Tasks.objects.filter(project__name__icontains=name, end_date__gte=begin_date, end_date__lte=end_date).count()

        else:
            active = Projects.objects.filter(status__in=['active', 'Active'],
                                             end_date_format__range=[first,
                                                                     last]).count()
            closed = Projects.objects.filter(status__in=['Completed', 'completed'],
                                             end_date_format__range=[first,
                                                                     last]).count()

            date_today = datetime.datetime.now().date()
            week_day = date_today.weekday()
            begin_date = datetime.datetime.now().date() - datetime.timedelta(
                days=week_day)
            end_date = datetime.datetime.now().date() + datetime.timedelta(
                days=4 - week_day)
            this_week = Tasks.objects.filter(end_date__gte=begin_date,
                                             end_date__lte=end_date).count()

        month = datetime.datetime.strftime(today, "%B")
        project.sort(key=lambda hotel: hotel['csm'])
        red, yellow, green = 0,0,0
        for pro in project:
            if pro['status'] in ["Active",
                              'active'] and pro['end_date'] and pro['end_date'] < today:
                red += 1
            elif pro['status'] in ["Active",
                                'active'] and pro['end_date'] == None:
                red += 1
            elif pro['status'] in ["closed",
                                'Closed'] and pro['end_date'] == None:
                red += 1
            elif pro['status'] in ["Active",
                                'active'] and pro['end_date'] >= today:
                yellow += 1
            else:
                green += 1
        if name == "hdfc":
            return render(request, "zohouser/project_list_pie_hdfc.html",
                          {"projects": project,
                           "csm": list(set(csm_list)),
                           "date": today,
                           "name": name,
                           "status": status,
                           "user_name": user.email,
                           "total_projects": total_projects,
                           "active": active,
                           "closed": closed,
                           "task_closed": green,
                           "task_open": red,
                           "task_inprogress": yellow,
                           "this_week": this_week,
                           "month": month
                           })
        else:
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
                           "task_closed": green,
                           "task_open": red,
                           "task_inprogress": yellow,
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
            tasks = all_project_task_list()
            return HttpResponse("success")
            # return redirect("/time_sheet_pull/")
    else:
        return redirect("/")


def tasks_pull(request):
    user = request.user
    if user.is_authenticated:
        code = request.GET.get("code", "")
        name = request.GET.get("name", "")
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
            tasks = all_projects_task(user, name)
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
            tasks = Tasks.objects.all()
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
        name = request.GET.get("name", "")

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
            milestone = all_projects_milestone(user=user,name=name)
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
        name = request.GET.get("name", "")
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
            timesheet = all_project_time_sheet(user=user, name=name)
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
        time_users = TimeSheet.objects.all().values_list("owner_name")
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
        mile = Milestone.objects.filter(id=milestone)
        if mile:
            mile= mile[0]
            project = mile.project
            today =datetime.datetime.now().date()
            task = Tasks.objects.filter(milestone_id=mile.id_string)
            closed_tasks = Tasks.objects.filter(milestone_id=mile.id_string, status__in=["closed", "Closed"]).count()
            active_tasks = Tasks.objects.filter(milestone_id=mile.id_string, status__in=["Open", "open", 'In Progress', "in progress", "In progress"]).count()
            response = []
            # green = Tasks.objects.filter(milestone_id=mile.id_string,status__in=["closed","Closed"]).count()
            # red = Tasks.objects.filter(milestone_id=mile.id_string,status__in=["Open", "open",'In Progress',"in progress","In progress"],
            #                                     end_date__lt=today).count()
            # yellow = Tasks.objects.filter(milestone_id=mile.id_string,status__in=["Open", "open",'In Progress',"in progress","In progress"],
            #                                         end_date__gte=today).count()
            green, red, yellow = 0,0,0
            date_today = datetime.datetime.now().date()
            week_day = date_today.weekday()
            begin_date = datetime.datetime.now().date() - datetime.timedelta(
                days=week_day)
            end_date = datetime.datetime.now().date() + datetime.timedelta(
                days=4 - week_day)
            this_week = Tasks.objects.filter(milestone_id=mile.id_string,end_date__gte=begin_date,
                                             end_date__lte=end_date).count()
            for t in task:
                user_list = t.zohousers_set.all()
                user = ",".join(list(set([u.username for u in user_list])))
                time_sheet_count = TimeSheet.objects.filter(task=t).count()
                try:
                    datetime.datetime.strftime(t.end_date,"%Y-%m-%d")
                    percent_complete = float(t.percent_complete)
                    if percent_complete >= 85:
                        green += 1
                        status = "closed"
                    elif 75.0 <= percent_complete < 85 or t.end_date > today:
                        yellow += 1
                        status = "progress"
                    else:
                        red += 1
                        status = "over"
                    # if t.status in ["open", 'Open', 'In Progress', "In progress"] and t.end_date > today:
                    # elif t.status in ["open", 'Open'] and t.end_date < today:
                    # else:
                except Exception:
                    percent_complete = float(t.percent_complete)
                    if percent_complete >= 85:
                        green += 1
                        status = "closed"
                    elif 75.0 <= percent_complete < 85 :
                        yellow += 1
                        status = "progress"
                    else:
                        red += 1
                        status = "over"

                response.append(dict(
                    project=project.name,
                    owner_name=mile.owner_name,
                    name=mile.name,
                    status=mile.status,
                    start_date=mile.start_date,
                    end_date=mile.end_date,
                    sequence=mile.sequence,
                    flag=mile.flag,
                    users=user,
                    time_sheet=time_sheet_count,
                    task_status=status,
                    task_name=t.task_name,
                    completed=t.completed,
                    percent_complete=t.percent_complete
                ))
            return render(request, "zohouser/tasks/project_tasks.html",
                          {"current_task": response,
                           "name": project.name + "(" +mile.name + ")",
                           "total_projects":task.count(),
                           "closed":closed_tasks,
                           "active": active_tasks,
                           "mile_id": mile.id,
                           "task_open":red,
                           "task_inprogress": yellow,
                           "task_closed": green,
                           "this_week":this_week,
                            "proj_id": project.id

            })
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
            task_active = Tasks.objects.filter(end_date__gte=begin_date,
                                               end_date__lte=end_date,
                                               status__in=['Open', "In Progress"]).count()
            task_close = Tasks.objects.filter(end_date__gte=begin_date,
                                           end_date__lte=end_date,
                                           status__in=['Closed', "closed"]).count()
            task_over = Tasks.objects.filter(
                status__in=['Open', "In Progress"],
                end_date__gte=begin_date,
                end_date__lt=date_today).count()
            task_progress = Tasks.objects.filter(status__in=['Open',
                                                             "In Progress"],
                                                 end_date__gte=date_today,
                                                 end_date__lte=end_date).count()

        else:
            this_week = Tasks.objects.filter(project__name__icontains=name,
                                             end_date__gte=begin_date,
                                             end_date__lte=end_date)
            task_active = Tasks.objects.filter(end_date__gte=begin_date,project__name__icontains=name,
                                               end_date__lte=end_date,
                                               status__in=['Open',
                                                           "In Progress"]).count()
            task_close = Tasks.objects.filter(end_date__gte=begin_date,project__name__icontains=name,
                                              end_date__lte=end_date,
                                              status__in=['Closed', "closed"]).count()
            task_over = Tasks.objects.filter(
                status__in=['Open', "In Progress"],
                end_date__gte=begin_date,
                end_date__lte=date_today,project__name__icontains=name,).count()
            task_progress = Tasks.objects.filter(status__in=['Open',
                                                             "In Progress"],
                                                 end_date__gte=date_today,
                                                 end_date__lte=end_date,project__name__icontains=name).count()
        tasks = filter_tasks(this_week)
        tasks.sort(key=lambda hotel: hotel['status'], reverse=True)
        return render(request, "zohouser/task_wise_list.html",{
            "tasks": tasks,
            "total_projects": len(tasks),
            "active": task_active,
            "closed": task_close,
            "task_open":task_over,
            "task_inprogress":task_progress,
            "task_closed":task_close,
            "name": "all" if "indigo" in user.email else "hdfc"

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
            percent = pro['percent']
            if percent >= 85.0:
                green_project.append(pro)
            elif 75.0 <= percent < 85.0:
                yellow_project.append(pro)
            else:
                red_project.append(pro)
        # color = color.split(",")
        if color == "red":
            print "red"
            return render(request, "zohouser/filter_new_red.html",
                      {"projects": red_project,
                       "csm": list(set(csm_list)),
                       "date": today,
                       "user_name": user.email,
                       "total_projects": total_projects,
                       "color": color

                       })
        elif color == "yellow":
            print "yellow"

            return render(request, "zohouser/filter_new_orange.html",
                          {"projects": yellow_project,
                           "csm": list(set(csm_list)),
                           "date": today,
                           "user_name": user.email,
                           "total_projects": total_projects,
                           "color": color

                           })
        elif color == "green":
            print "green"

            return render(request, "zohouser/filter_new_green.html",
                          {"projects": green_project,
                           "csm": list(set(csm_list)),
                           "date": today,
                           "user_name": user.email,
                           "total_projects": total_projects,
                           "color": color

                           })
        elif color == "red,green":
            print "red,green"

            return render(request, "zohouser/filter_new_red_green.html",
                          {"projects": red_project + green_project,
                           "csm": list(set(csm_list)),
                           "date": today,
                           "user_name": user.email,
                           "total_projects": total_projects,
                           "color": color

                           })
        elif color == "red,yellow":
            print "red,yellow"

            return render(request, "zohouser/filter_new_red_yellow.html",
                          {"projects": red_project + yellow_project,
                           "csm": list(set(csm_list)),
                           "date": today,
                           "user_name": user.email,
                           "total_projects": total_projects,
                           "color": color

                           })
        elif color == "yellow,green":
            print "yellow,green", len(yellow_project + green_project)
            return render(request, "zohouser/filter_new_yellow_green.html",
                          {"projects": yellow_project + green_project,
                           "csm": list(set(csm_list)),
                           "date": today,
                           "user_name": user.email,
                           "total_projects": total_projects,
                           "color": color

                           })

        else:
            print "all"

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
    today = datetime.datetime.now().date()
    first, last = get_month_day_range(today)
    tasks_data = request.GET.get("tasks")
    if user.is_authenticated():
        if tasks_data:
            if name == "all":
                tasks = Tasks.objects.filter(status__in=['open',
                                                             'Open','in progress','In Progress'])
            else:
                tasks = Tasks.objects.filter(project__name__icontains=name,
                                             status__in=['open','Open','in progress','In Progress'])
        else:
            if name == "all":
                tasks = Tasks.objects.filter(status__in=['open','Open','in progress','In Progress'], end_date__gte=first, end_date__lt=today)
            else:
                tasks = Tasks.objects.filter(project__name__icontains=name,
                                             status__in=['open','Open', 'in progress','In Progress'],  end_date__gte=first, end_date__lt=today)
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
    tasks_data = request.GET.get("tasks")
    if user.is_authenticated():
        today = datetime.datetime.now().date()
        first, last = get_month_day_range(today)
        if tasks_data:
            if name == 'all':
                tasks = Tasks.objects.filter(
                    status__in=['in progress',
                                'In Progress'])
            else:
                tasks = Tasks.objects.filter(
                    project__name__icontains=name,
                    status__in=['in progress',
                                'In Progress'])
        else:
            if name == 'all':
                tasks = Tasks.objects.filter(
                    status__in=['in progress','In Progress'],  end_date__range=[today,last])
            else:
                tasks = Tasks.objects.filter(
                    project__name__icontains=name,
                    status__in=['in progress',
                                'In Progress'], end_date__range=[today,last])
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
    tasks_data = request.GET.get("tasks")
    today = datetime.datetime.now().date()
    first, last = get_month_day_range(today)
    if user.is_authenticated():
        if tasks_data:
            if name == 'all':
                tasks = Tasks.objects.filter(status__in=['closed',
                                                           'Closed'])
            else:
                tasks = Tasks.objects.filter(project__name__icontains=name,
                                                   status__in=['closed',
                                                               'Closed'])
        else:
            if name == 'all':
                tasks = Tasks.objects.filter(status__in=['closed',
                                                     'Closed'],
                                             last_updated_time__range=[first, last])
            else:
                tasks = Tasks.objects.filter(project__name__icontains=name,
                                         status__in=['closed',
                                                     'Closed'],
                                             last_updated_time__range=[first, last])
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


def show_all(request):
    user = request.user
    if user.is_authenticated():
        name = request.GET.get('name')
        status = request.GET.get('status')
        csms = request.GET.get('csm')
        color = request.GET.get('color')
        csm_data = Projects.objects.all().values_list("owner_name")
        csm_list = []
        for c in csm_data:
            names = str(c[0])
            if names not in csm_data:
                csm_list.append(names)
        if color:
            project = project_list_view_color(name, csms, color)
        else:
            project = project_list_view_all(name, status, csms)
        sorted(list(set(csm_list)))
        total_projects = len(project)
        if name == "hdfc":
            active = Projects.objects.filter(name__icontains=name,
                                             status__in=['active', 'Active'],).count()
            # closed = Projects.objects.filter(name__icontains=name,
            #                                  status__in=['Completed', 'completed'],).count()
            # task_open = Tasks.objects.filter(project__name__icontains=name,
            #                                  status__in=['open', 'Open',
            #                                              'in progress',
            #                                              'In Progress']).count()
            # task_inprogress = Tasks.objects.filter(
            #     project__name__icontains=name,
            #     status__in=['in progress',
            #                 'In Progress']).count()
            # task_closed = Tasks.objects.filter(project__name__icontains=name,
            #                                    status__in=['closed',
            #                                                'Closed'],
            #                                    ).count()
            date_today = datetime.datetime.now().date()
            week_day = date_today.weekday()
            begin_date = datetime.datetime.now().date() - datetime.timedelta(
                days=week_day)
            end_date = datetime.datetime.now().date() + datetime.timedelta(
                days=4 - week_day)
            this_week = Tasks.objects.filter(project__name__icontains=name,
                                             end_date__gte=begin_date,
                                             end_date__lte=end_date).count()


        else:
            active = Projects.objects.filter(status__in=['active', 'Active']).count()
            # closed = Projects.objects.filter(status__in=['Completed', 'completed'],).count()
            # task_open = Tasks.objects.filter(
            #     status__in=['open', 'Open', 'in progress', 'In Progress']).count()
            # task_inprogress = Tasks.objects.filter(status__in=['in progress',
            #                                                    'In Progress']).count()
            # task_closed = Tasks.objects.filter(status__in=['Closed',
            #                                                'closed']).count()
            date_today = datetime.datetime.now().date()
            week_day = date_today.weekday()
            begin_date = datetime.datetime.now().date() - datetime.timedelta(
                days=week_day)
            end_date = datetime.datetime.now().date() + datetime.timedelta(
                days=4 - week_day)
            this_week = Tasks.objects.filter(end_date__gte=begin_date,
                                             end_date__lte=end_date).count()
        project.sort(key=lambda hotel: hotel['color'], reverse=True)
        red, yellow, green = 0, 0, 0
        today = datetime.datetime.now().date()
        for pro in project:
            if pro['status'] in ["Active",
                                 'active'] and pro['end_date'] and pro[
                'end_date'] < today:
                red += 1
            elif pro['status'] in ["Active",
                                   'active'] and pro['end_date'] == None:
                red += 1
            elif pro['status'] in ["closed",
                                   'Closed'] and pro['end_date'] == None:
                red += 1
            elif pro['status'] in ["Active",
                                   'active', "In Progress"] and pro['end_date'] >= today:
                yellow += 1
            else:
                green += 1
        if name == "hdfc":

            return render(request, "zohouser/project_list_pie_all_hdfc.html",
                      {"projects": project,
                       "csm": list(set(csm_list)),
                       "name": name,
                       "status": status,
                       "user_name": user.email,
                       "total_projects": total_projects,
                       "active": red + yellow,
                       "closed": green,
                       "task_closed": green,
                       "task_open": red,
                       "task_inprogress": yellow,
                       "this_week": this_week,
                       })
        else:
            return render(request, "zohouser/project_list_pie_all.html",
                          {"projects": project,
                           "csm": list(set(csm_list)),
                           "name": name,
                           "status": status,
                           "user_name": user.email,
                           "total_projects": total_projects,
                           "active": red + yellow,
                           "closed": green,
                           "task_closed": green,
                           "task_open": red,
                           "task_inprogress": yellow,
                           "this_week": this_week,
                           })


def client_tasks_all(request, name):
    if name == "all":
        task_open = Tasks.objects.filter(status__in=['open', 'Open', 'in progress','In Progress']).count()
        task_inprogress = Tasks.objects.filter(status__in=['in progress',
                                                           'In Progress']).count()
        task_closed = Tasks.objects.filter(status__in=['Closed', 'closed',"close", "close"]).count()
    else:
        task_open = Tasks.objects.filter(project__name__icontains=name,
                                         status__in=['open', 'Open', 'in progress','In Progress']).count()
        task_inprogress = Tasks.objects.filter(project__name__icontains=name,
                                               status__in=['in progress',
                                                           'In Progress']).count()
        task_closed = Tasks.objects.filter(project__name__icontains=name,
                                           status__in=['Closed', 'closed',"close", "close"]).count()

    return HttpResponse(json.dumps(dict(task_open=task_open, task_inprogress=task_inprogress,task_closed=task_closed)))


def project_pie(request):
    user = request.user
    red, green, yellow = 0, 0, 0
    today = datetime.datetime.now().date()
    first, last = get_month_day_range(today)
    if "indigo" in user.email:
        projects = Projects.objects.filter(end_date_format__range=[first, last])
    else:
        projects = Projects.objects.filter(name__icontains='hdfc', end_date_format__range=[first, last])
    red, yellow, green = 0,0,0
    for pro in projects:
        # close_tasks = pro.task_count_close
        # total_tasks = pro.task_count_close + pro.task_count_open
        # percent = round(close_tasks / total_tasks, 2) * 100
        if pro.status in ["Active",
                          'active'] and pro.end_date_format and pro.end_date_format < today:
            red += 1
        elif pro.status in ["Active",
                            'active'] and pro.end_date_format == None:
            red += 1
        elif pro.status in ["closed",
                            'Closed'] and pro.end_date_format == None:
            red += 1
        elif pro.status in ["Active",
                            'active'] and pro.end_date_format >= today:
            yellow += 1
        else:
            green += 1
    return HttpResponse(json.dumps(dict(red=red, green=green, yellow=yellow)))


def project_pie_all(request):
    user = request.user
    red, green, yellow = 0, 0, 0
    if "indigo" in user.email:
        projects = Projects.objects.all()
    else:
        projects = Projects.objects.filter(name__icontains='hdfc')
    today = datetime.datetime.now().date()
    for pro in projects:
        # close_tasks = pro.task_count_close
        # total_tasks = pro.task_count_close + pro.task_count_open
        # percent = round(close_tasks / total_tasks, 2) * 100
        if pro.status in ["Active",
                          'active'] and pro.end_date_format and pro.end_date_format < today:
            red += 1
        elif pro.status in ["Active",
                            'active'] and pro.end_date_format == None:
            red += 1
        elif pro.status in ["closed",
                            'Closed'] and pro.end_date_format == None:
            red += 1
        elif pro.status in ["Active",
                            'active'] and pro.end_date_format >= today:
            yellow += 1
        else:
            green += 1

    return HttpResponse(json.dumps(dict(red=red, green=green, yellow=yellow)))


def projects_types(request):
    user = request.user
    if user.is_authenticated():
        red, green, yellow = [],[],[]
        name = request.GET.get("project_name")
        month = request.GET.get("month", "all")
        today = datetime.datetime.now().date()
        first, last = get_month_day_range(today)
        project_type=request.GET.get("type")
        if month == "all":
            if name != "all":
                projects = Projects.objects.filter(name__icontains=name,)
            else:
                projects = Projects.objects.all()

        else:
            if name != "all":
                projects = Projects.objects.filter(name__icontains=name, end_date_format__range=[first,last])

            else:
                projects = Projects.objects.filter(end_date_format__range=[first,last])

        for p in projects:
            today = datetime.datetime.now().date()
            if p.status in ["Active",
                              'active'] and p.end_date_format and p.end_date_format < today:
                red.append(p)
            elif p.status in ["Active",
                                'active'] and p.end_date_format == None:
                red.append(p)
            elif p.status in ["closed",
                                'Closed'] and p.end_date_format == None:
                red.append(p)
            elif p.status in ["Active", 'active',
                                'In Progress'] and p.end_date_format and p.end_date_format > today:
                yellow.append(p)
            else:
                green.append(p)
            # try:
            #     total = p.task_count_open + p.task_count_close
            #     percent = float(round(p.task_count_close/total, 2) * 100)
            # except ZeroDivisionError:
            #     percent = 0
            # if (percent >= 85.0 and p.end_date_format) or p.status == "completed":
            #     green.append(p)
            # elif 75.0 <= percent < 85.0:
            #     try:
            #         d = datetime.datetime.strftime(p.end_date_format,'%Y-%m-%d')
            #         if p.end_date_format > today:
            #             yellow.append(p)
            #         else:
            #             red.append(p)
            #     except Exception:
            #         red.append(p)
            # else:
                red.append(p)

        if project_type == 'red':
            projects = project_filter_data(red)
            status="Overdue Projects"
            color="red"

            # return render(request, "projects.html", {"project": projects})
        elif project_type == 'yellow':
            projects = project_filter_data(yellow)
            status = "In-Progress Projects"
            color="yellow"

            # return render(request, "projects.html", {"project": projects})
        else:
            projects = project_filter_data(green)
            status = "Completed Projects"
            color="green"
        week_day = today.weekday()
        begin_date = datetime.datetime.now().date() - datetime.timedelta(
            days=week_day)
        end_date = datetime.datetime.now().date() + datetime.timedelta(
            days=6 - week_day)
        this_week = Tasks.objects.filter(end_date__gte=begin_date,end_date__lte=end_date).count()
        if name == "hdfc":

            return render(request, "zohouser/projects_hdfc.html", {"projects": projects,
                                                          "status": status,
                                                          "color": color,
                                                          "this_week":this_week
                                                          })
        else:
            return render(request, "zohouser/projects.html",
                          {"projects": projects,
                           "status": status,
                           "color": color,
                           "this_week": this_week
                           })


def mile_stone_pie(request, project_id):
    project = Projects.objects.get(id=project_id)
    date_today = datetime.datetime.now().date()
    over_due_ms = project.milestone_set.filter(end_date__lt=date_today,
                                               status='notcompleted').count()
    pending_ms = project.milestone_set.filter(end_date__gte=date_today,
                                              status='notcompleted').count()
    completed_ms = project.milestone_set.filter(status='completed').count()
    return HttpResponse(json.dumps(dict(green=completed_ms,yellow=pending_ms, red=over_due_ms)))


def task_pie(request, project_id):
    user = request.user
    if user.is_authenticated():
        mile = Milestone.objects.get(id=project_id)
        today = datetime.datetime.now().date()
        task = Tasks.objects.filter(milestone_id=mile.id_string)
        reen, red, yellow = 0, 0, 0
        date_today = datetime.datetime.now().date()
        week_day = date_today.weekday()
        begin_date = datetime.datetime.now().date() - datetime.timedelta(
            days=week_day)
        end_date = datetime.datetime.now().date() + datetime.timedelta(
            days=4 - week_day)
        red, green, yellow = 0,0,0
        for t in task:

            try:
                datetime.datetime.strftime(t.end_date, "%Y-%m-%d")
                percent_complete = float(t.percent_complete)
                if percent_complete >= 85:
                    green += 1
                elif 75.0 <= percent_complete < 85 or t.end_date > today:
                    yellow += 1
                else:
                    red += 1
                # if t.status in ["open", 'Open', 'In Progress', "In progress"] and t.end_date > today:
                # elif t.status in ["open", 'Open'] and t.end_date < today:
                # else:
            except Exception:
                percent_complete = float(t.percent_complete)
                if percent_complete >= 85:
                    green += 1
                    status = "closed"
                elif 75.0 <= percent_complete < 85:
                    yellow += 1
                    status = "progress"
                else:
                    red += 1
                    status = "over"

        return HttpResponse(json.dumps(dict(red=red, green=green, yellow=yellow)))
    else:
        return redirect("/")


def task_pie_project(request, project_id):
    user = request.user
    if user.is_authenticated():
        project = Projects.objects.get(id=project_id)
        today = datetime.datetime.now().date()
        tasks = project.tasks_set.all()
        red, yellow, green = 0, 0, 0
        for t in tasks:
            if t.status in ["Open", "In Progress", "open",
                            "in progress"] and t.end_date and t.end_date < today:
                red += 1
            elif t.status in ["Open", "In Progress",
                              "open"] and t.end_date == None:
                red += 1
            elif t.status in ["closed", 'Closed'] and t.end_date == None:
                green += 1
            elif t.status in ["Open", "In Progress", "open",
                              'in progress'] and t.end_date and t.end_date > today:
                yellow += 1
            else:
                green += 1
        # closed_tasks = project.tasks_set.filter(status__in=["closed","Closed"]).count()
        # active_tasks = project.tasks_set.filter(
        #                                     status__in=["Open", "open",'In Progress',"in progress","In progress"],end_date__lt=today).count()
        # inprogress_tasks = project.tasks_set.filter(status__in=["Open", "open",'In Progress', "in progress","In progress"],end_date__gte=today).count()
        return HttpResponse(json.dumps(dict(red=red, green=green, yellow=yellow)))
    else:
        return redirect("/")


def fetch_mile_stones(request,project_id):
    project = Projects.objects.get(id=project_id)
    date_today = datetime.datetime.now().date()
    status=request.GET.get('type')
    tasks = project_all_milestone(project_id)
    red,yellow,green = [],[],[]
    for t in tasks:
        if t['end_date'] < date_today and t['status'] == 'notcompleted':
            red.append(t)
        elif t['end_date'] >= date_today and t['status'] == 'notcompleted':
            yellow.append(t)
        else:
            green.append(t)
    if status == "red":
        mile_stones = red
    elif status == "yellow":

        mile_stones = yellow
    else:
        mile_stones = green

    return render(request, "zohouser/mile_stone.html", {"milestone": mile_stones, "name": project.name})


def mile_stone_filter_tasks(request, milestone):
    user = request.user
    if user.is_authenticated():
        mile = Milestone.objects.get(id=milestone)
        style = request.GET.get("type")
        project = mile.project
        user = ""
        today =datetime.datetime.now().date()
        week_day = today.weekday()
        begin_date = datetime.datetime.now().date() - datetime.timedelta(
            days=week_day)
        end_date = datetime.datetime.now().date() + datetime.timedelta(
            days=6 - week_day)
        response = []
        if style == "red":
            task = Tasks.objects.filter(milestone_id=mile.id_string,status__in=["Open", "open",'In Progress',"in progress","In progress"],
                                            end_date__lt=today)
        elif style == 'yellow':
            task = Tasks.objects.filter(milestone_id=mile.id_string,status__in=["Open", "open",'In Progress',"in progress","In progress"],
                                                end_date__gte=today)
        else:
            task = Tasks.objects.filter(milestone_id=mile.id_string,status__in=["closed","Closed"])
        for t in task:
            user_list = t.zohousers_set.all()
            user = ",".join(list(set([u.username for u in user_list])))
            time_sheet_count = TimeSheet.objects.filter(task=t).count()
            if t.status in ["open", 'Open'] and t.end_date > today:
                status = "progress"
            elif t.status in ["open", 'Open'] and t.end_date < today:
                status = "over"
            else:
                status = "closed"
            response.append(dict(
                project=project.name,
                owner_name=mile.owner_name,
                name=mile.name,
                status=mile.status,
                start_date=mile.start_date,
                end_date=mile.end_date,
                sequence=mile.sequence,
                flag=mile.flag,
                users=user,
                time_sheet=time_sheet_count,
                task_status=status,
                task_name=t.task_name,
                # created_at=t.created_time,
                completed=t.completed,
                percent_complete=t.percent_complete
            ))
        return render(request, "zohouser/tasks/project_tasks_filter.html",
                      {"current_task": response,
                       "name": project.name + "(" +mile.name + ")",
                       "total_projects":task.count(),
                       "closed":closed_tasks,
                       "proj_id": mile.id,


        })
    else:
        return redirect("/")


def project_task_filter(request, project_id):
    user = request.user
    if user.is_authenticated():
        style = request.GET.get("type")
        project = Projects.objects.get(id=project_id)
        date_today = datetime.datetime.now().date()
        tasks = project.tasks_set.all()
        red, yellow, green = [],[],[]
        today = datetime.datetime.now().date()
        for t in tasks:
            if t.status in ["Open", "In Progress", "open",
                            "in progress"] and t.end_date and t.end_date < today:
                red.append(t)
            elif t.status in ["Open", "In Progress",
                              "open"] and t.end_date == None:
                red.append(t)
            elif t.status in ["closed", 'Closed'] and t.end_date == None:
                green.append(t)
            elif t.status in ["Open", "In Progress", "open",
                              'in progress'] and t.end_date and t.end_date > today:
                yellow.append(t)
            else:
                green.append(t)
        # if style == "red":
        #     tasks = project.tasks_set.filter(
        #         status__in=['Open', 'open', 'in progress', 'In Progress'],
        #         end_date__lt=date_today)
        # elif style == "yellow":
        #     tasks = project.tasks_set.filter(
        #         status__in=['Open', 'open', 'in progress', 'In Progress'],
        #         end_date__gte=date_today)
        # else:
        #     tasks = project.tasks_set.filter(
        #         status__in=['closed', 'Closed'])
        if style == 'red':
            tasks = red
        elif style == 'yellow':
            tasks = yellow
        else:
            tasks = green
        response = []
        for t in tasks:
            users = t.zohousers_set.all()
            time_sheet_count = TimeSheet.objects.filter(task=t).count()
            if t.status in ["Open", "In Progress", "open",
                            "in progress"] and t.end_date and t.end_date < today:
                status = 'over'
            elif t.status in ["Open", "In Progress",
                              "open"] and t.end_date == None:
                status = 'over'
            elif t.status in ["closed", 'Closed'] and t.end_date == None:
                status = 'closed'
            elif t.status in ["Open", "In Progress", "open",
                              'in progress'] and t.end_date and t.end_date > today:
                status = 'progress'
            else:
                status = 'closed'
            # try:
            #     datetime.datetime.strftime(t.end_date, "%Y-%m-%d")
            #
            #     if t.status in ["open", 'Open'] and t.end_date > today:
            #         status = "progress"
            #     elif t.status in ["open", 'Open'] and t.end_date < today:
            #         status = "over"
            #     else:
            #         status = "closed"
            # except Exception:
            #     status = "over"
            response.append(dict(
                id=t.id,
                description=strip_tags(t.description) if len(
                    strip_tags(t.description)) < 50 else strip_tags(
                    t.description)[:50] + "...",
                project_id=project.project_id,
                task_list_id=t.tasklist_id,
                task_id=t.task_id,
                start_date=t.start_date,
                end_date=t.end_date,
                status=t.status,
                task_name=t.task_name,
                created_by=t.created_person,
                created_time=t.created_time,
                completed=t.completed,
                percent_complete=t.percent_complete,
                completed_time=t.last_updated_time,
                subtasks=t.subtasks,
                project=t.project,
                owner=",".join(list(set([o.username for o in users]))),
                time_sheet_count=time_sheet_count,
                task_status=status
            ))

        return render(request, "zohouser/tasks/project_tasks_filter.html", {
            "date_today": date_today,
            "current_task": response,
            "name": "ALL Task {}".format(project.name),

            "proj_id": project.id
        })
    else:
        return redirect("/")


def task_weekly_pie(request):
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
            task_close = Tasks.objects.filter(end_date__gte=begin_date,
                                           end_date__lte=end_date,
                                           status__in=['Closed', "closed"]).count()
            task_over = Tasks.objects.filter(
                status__in=['Open', "In Progress"],
                end_date__gte=begin_date,
                end_date__lt=date_today).count()
            task_progress = Tasks.objects.filter(status__in=['Open',
                                                             "In Progress"],
                                                 end_date__gte=date_today,
                                                 end_date__lte=end_date).count()

        else:
            task_close = Tasks.objects.filter(end_date__gte=begin_date,project__name__icontains=name,
                                              end_date__lte=end_date,
                                              status__in=['Closed', "closed"]).count()
            task_over = Tasks.objects.filter(
                status__in=['Open', "In Progress"],
                end_date__gte=begin_date,
                end_date__lte=date_today,project__name__icontains=name,).count()
            task_progress = Tasks.objects.filter(status__in=['Open',
                                                             "In Progress"],
                                                 end_date__gte=date_today,
                                                 end_date__lte=end_date,project__name__icontains=name).count()

        # if style == 'red':
        #     tasks = filter_tasks(task_over)
        # elif style == 'yellow':
        #     tasks = filter_tasks(task_progress)
        # else:
        #     tasks = filter_tasks(task_close)

        # tasks.sort(key=lambda hotel: hotel['status'], reverse=True)
        return HttpResponse(json.dumps({
            "red": task_over,
            "green": task_close,
            "yellow":task_progress

        }))
    else:
        return redirect("/")


def week_task_view(request):
    user = request.user
    if user.is_authenticated():
        name = request.GET.get("project_name")
        style = request.GET.get("type")
        date_today = datetime.datetime.now().date()
        week_day = date_today.weekday()
        begin_date = datetime.datetime.now().date() - datetime.timedelta(
            days=week_day)
        end_date = datetime.datetime.now().date() + datetime.timedelta(
            days=6 - week_day)
        if name == "all":
            task_close = Tasks.objects.filter(end_date__gte=begin_date,
                                           end_date__lte=end_date,
                                           status__in=['Closed', "closed"])
            task_over = Tasks.objects.filter(
                status__in=['Open', "In Progress"],
                end_date__gte=begin_date,
                end_date__lt=date_today)
            task_progress = Tasks.objects.filter(status__in=['Open',
                                                             "In Progress"],
                                                 end_date__gte=date_today,
                                                 end_date__lte=end_date)

        else:
            task_close = Tasks.objects.filter(end_date__gte=begin_date,project__name__icontains=name,
                                              end_date__lte=end_date,
                                              status__in=['Closed', "closed"])
            task_over = Tasks.objects.filter(
                status__in=['Open', "In Progress"],
                end_date__gte=begin_date,
                end_date__lte=date_today,project__name__icontains=name,)
            task_progress = Tasks.objects.filter(status__in=['Open',
                                                             "In Progress"],
                                                 end_date__gte=date_today,
                                                 end_date__lte=end_date,project__name__icontains=name)

        if style == 'red':
            tasks = filter_tasks(task_over)
        elif style == 'yellow':
            tasks = filter_tasks(task_progress)
        else:
            tasks = filter_tasks(task_close)

        tasks.sort(key=lambda hotel: hotel['status'], reverse=True)
        return render(request, "zohouser/task_wise_list_type.html",{
            "tasks": tasks,

        })
    else:
        return redirect("/")


def project_task_current(request, project_id):
    user = request.user
    if user.is_authenticated():
        date_today = datetime.datetime.now().date()
        week_day = date_today.weekday()
        begin_date = datetime.datetime.now().date() - datetime.timedelta(
            days=week_day)
        end_date = datetime.datetime.now().date() + datetime.timedelta(
            days=6 - week_day)
        project = Projects.objects.get(id=project_id)
        this_week = project.tasks_set.filter(end_date__gte=begin_date,
                                         end_date__lte=end_date)
        task_active = project.tasks_set.filter(end_date__gte=begin_date,
                                           end_date__lte=end_date,
                                           status__in=['Open', "In Progress"]).count()
        task_close = project.tasks_set.filter(end_date__gte=begin_date,
                                       end_date__lte=end_date,
                                       status__in=['Closed', "closed"]).count()
        task_over = project.tasks_set.filter(
            status__in=['Open', "In Progress"],
            end_date__gte=begin_date,
            end_date__lt=date_today).count()
        task_progress = project.tasks_set.filter(status__in=['Open',
                                                         "In Progress"],
                                             end_date__gte=date_today,
                                             end_date__lte=end_date).count()


        tasks = filter_tasks(this_week)
        tasks.sort(key=lambda hotel: hotel['status'], reverse=True)
        return render(request, "zohouser/task_wise_list.html",{
            "tasks": tasks,
            "total_projects": len(tasks),
            "active": task_active,
            "closed": task_close,
            "task_open":task_over,
            "task_inprogress":task_progress,
            "task_closed":task_close,
            "name": "all" if "indigo" in user.email else "hdfc"

        })
    else:
        return redirect("/")



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


