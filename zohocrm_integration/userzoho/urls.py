"""zohocrm_integration URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^callback/', callback),
    url(r'^detail/(?P<project_id>\w+)', task_list),
    url(r'^time_sheet_task/(?P<task_id>\w+)', time_sheet_task),
    url(r'^time_sheet/(?P<project_id>\w+)', time_sheet_projects_tasks),
    url(r'^project_detail/(?P<project_id>\w+)', project_detail),
    url(r'^open_task/(?P<project_id>\w+)', open_tasks),
    url(r'^close_task/(?P<project_id>\w+)', close_tasks),
    url(r'^all_tasks/(?P<project_id>\w+)', all_tasks),
    url(r'^all_milestone/(?P<project_id>\w+)', all_milestone),
    url(r'^open_milestone/(?P<project_id>\w+)', open_milestone),
    url(r'^close_milestone/(?P<project_id>\w+)', close_milestone),
    url(r'^mile_stone_task/(?P<milestone>\w+)', mile_stone_tasks),
    url(r'^client_tasks/(?P<name>\w+)', client_tasks),
    url(r'^project_list/', project_list),

    # URL for auth request
    url(r'^task/(?P<project_id>\w+)', task_project),
    url(r'^milestone/(?P<project_id>\w+)', milestone_data),
    url(r'^auth_request/', auth_request),
    url(r'^clients/', client_list,name="clients"),
    url(r'^projects/', projects, name="projects"),
    url(r'^projects_grantt/', projects_grantt, name="projects_grantt"),
    url(r'^grant_view/', projects_grant, name="grant_view"),
    url(r'^login_user/', login_user, name='login_user'),
    url(r'^logout_user/', logout_user, name='logout_user'),
    url(r'^register_user/', register_user, name='register'),
    url(r'^projects_pull/', projects_pull, name='projects_pull'),
    url(r'^time_sheet_pull/', time_sheet_pull, name='time_sheet_pull'),
    url(r'^tasks_pull/', tasks_pull, name='tasks_pull'),
    url(r'^milestone_pull/', milestone_pull, name='milestone_pull'),
    url(r'^resource_utilization/', resource_utilization, name='resource_utilization'),
    url(r'^time_sheet_range/', time_sheet_range, name='time_sheet_range'),
    url(r'^project_task_list/(?P<project_id>\w+)', task_list_projects, name='task_list_projects'),
    url(r'^sub_tasks/(?P<task_id>\w+)', sub_tasks, name='sub_tasks'),
    url(r'^task_bifurcate/(?P<project_id>\w+)', task_bifurcate, name='task_bifurcate'),
    url(r'^project/task/time_sheet/(?P<task_id>\w+)', project_task_time_sheet, name='project_task_time_sheet'),
    url(r'^project_filter/', project_filter, name='project_filter'),
    url(r'^status_check/', intermediate, name="intermediate"),
    url(r'^', home),

]
