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
    url(r'^open_milestone/(?P<project_id>\w+)', open_milestone),
    url(r'^close_milestone/(?P<project_id>\w+)', close_milestone),
    url(r'^project_list/(?P<name>\w+)', project_list),

    # URL for auth request
    url(r'^task/(?P<project_id>\w+)', task_project),
    url(r'^milestone/(?P<project_id>\w+)', milestone_data),
    url(r'^auth_request/', auth_request),
    url(r'^clients/', client_list),
    url(r'^projects/', projects, name="projects"),
    url(r'^login_user/', login_user, name='login_user'),
    url(r'^logout_user/', logout_user, name='logout_user'),
    url(r'^register_user/', register_user, name='register'),
    url(r'^', home),

]
