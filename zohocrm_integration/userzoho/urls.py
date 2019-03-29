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
    url(r'^mile_stone_filter_tasks/(?P<milestone>\w+)', mile_stone_filter_tasks),
    url(r'^client_tasks/(?P<name>\w+)', client_tasks),
    url(r'^client_tasks_all/(?P<name>\w+)', client_tasks_all),
    url(r'^project_list/', project_list),
    url(r'^project_list_running/', project_list_running),
    url(r'^show_all/', show_all),
    url(r'^closed_tasks/', closed_tasks),
    url(r'^pending_task/', pending_task),
    url(r'^over_due_task/', over_due_task),


    # URL for auth retasks_pullquest
    url(r'^task/(?P<project_id>\w+)', task_project),
    url(r'^milestone/(?P<project_id>\w+)', milestone_data),
    url(r'^project_ux/(?P<project_id>\w+)', project_ux),
    url(r'^project_ui/(?P<project_id>\w+)', project_ui),
    url(r'^project_html/(?P<project_id>\w+)', project_html),
    url(r'^project_api/(?P<project_id>\w+)', project_api),
    url(r'^project_bee/(?P<project_id>\w+)', project_bee),
    url(r'^project_qc/(?P<project_id>\w+)', project_qc),
    url(r'^project_uat/(?P<project_id>\w+)', project_uat),
    url(r'^auth_request/', auth_request),
    url(r'^clients/', client_list,name="clients"),
    # url(r'^projects/', projects, name="projects"),
    url(r'^projects/', projects_types, name="projects"),
    url(r'^projects_grantt/', projects_grantt, name="projects_grantt"),
    url(r'^grant_view/', projects_grant, name="grant_view"),
    url(r'^login_user/', login_user, name='login_user'),
    url(r'^logout_user/', logout_user, name='logout_user'),
    url(r'^register_user/', register_user, name='register'),
    url(r'^projects_pull/', projects_pull, name='projects_pull'),
    url(r'^time_sheet_pull/', time_sheet_pull, name='time_sheet_pull'),
    url(r'^tasks_pull/', tasks_pull, name='tasks_pull'),
    url(r'^sub_tasks_pull/', sub_tasks_pull, name='sub_tasks_pull'),
    url(r'^tasks_list_pull/', tasks_list_pull, name='tasks_list_pull'),
    url(r'^milestone_pull/', milestone_pull, name='milestone_pull'),
    url(r'^resource_utilization/', resource_utilization, name='resource_utilization'),
    url(r'^time_sheet_range/', time_sheet_range, name='time_sheet_range'),
    url(r'^project_task_list/(?P<project_id>\w+)', task_list_projects, name='task_list_projects'),
    url(r'^sub_tasks/(?P<task_id>\w+)', sub_tasks, name='sub_tasks'),
    url(r'^task_bifurcate/(?P<project_id>\w+)', task_bifurcate, name='task_bifurcate'),
    url(r'^project/task/time_sheet/(?P<task_id>\w+)', project_task_time_sheet, name='project_task_time_sheet'),
    url(r'^client_tasks_week/', task_weekly, name='task_weekly'),
    url(r'^project_filter/', project_filter, name='project_filter'),
    url(r'^project_filter_csm/', project_filter_csm, name='project_filter_csm'),
    url(r'^status_check/', intermediate, name="intermediate"),
    url(r'^project_list_color/', project_list_color, name="project_list_color"),
    url(r'^project_pie/', project_pie, name="project_pie"),
    url(r'^project_pie_hdfc/', project_pie_hdfc, name="project_pie_hdfc"),
    url(r'^week_task_view/', week_task_view, name="week_task_view"),
    url(r'^project_pie_all/', project_pie_all, name="project_pie_all"),
    url(r'^mile_stone_pie/(?P<project_id>\w+)/', mile_stone_pie, name="mile_stone_pie"),
    url(r'^task_weekly_pie/', task_weekly_pie, name="task_weekly_pie"),
    url(r'^task_pie/(?P<project_id>\w+)/', task_pie, name="task_pie"),
    url(r'^task_pie_project/(?P<project_id>\w+)/', task_pie_project, name="task_pie_project"),
    url(r'^project_task_filter/(?P<project_id>\w+)/', project_task_filter, name="project_task_filter"),
    url(r'^fetch_mile_stones/(?P<project_id>\w+)/', fetch_mile_stones, name="fetch_mile_stones"),
    url(r'^project_task_current/(?P<project_id>\w+)/', project_task_current, name="project_task_current"),
    url(r'^csm_list/', csm_list, name="csm_list"),
    url(r'^', home),

]
