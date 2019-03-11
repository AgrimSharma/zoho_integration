    # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *


class TokenAdmin(admin.ModelAdmin):
    list_display = ['access_token', "created_at"]


class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name', "owner_name", "project_id"]
    list_display = ['project_id', "name", "status"]


class ZohoUserAdmin(admin.ModelAdmin):
    raw_id_fields = ['tasks']
    def task(self, obj):
        return obj.tasks.task_name
    list_display = ['username', "task"]


class TaskAdmin(admin.ModelAdmin):
    raw_id_fields = ['project']

    def projects(self,obj):
        return obj.project.name

    list_display = ['projects', "task_id", "milestone_id", "task_name", "start_date", "end_date"]
    search_fields = ['project__name',"milestone_id", "task_id", "status", "task_name"]


class SubTaskAdmin(admin.ModelAdmin):
    raw_id_fields = ['tasks']

    def tasks(self,obj):
        return obj.tasks.task_name

    list_display = ['tasks', "sub_task_id", "duration", "completed", "start_date", "end_date"]
    search_fields = ['tasks__task_name',"sub_task_id"]


class TimeSheetAdmin(admin.ModelAdmin):
    raw_id_fields = ['project', "task"]

    def projects(self, obj):
        return obj.project.name

    def tasks(self, obj):
        return obj.task.task_name
    list_display = ['projects', "tasks", "owner_name", "total_minutes"]
    search_fields = ['project__name', "owner_name", "task__task_name"]


class MilestoneAdmin(admin.ModelAdmin):
    raw_id_fields = ['project']

    def projects(self, obj):
        return obj.project.name

    list_display = ['projects', "name", "start_date", "end_date"]
    search_fields = ['project__name']


class TaskListAdmin(admin.ModelAdmin):
    raw_id_fields = ['project']

    def projects(self, obj):
        return obj.project.name

    list_display = ['projects', "name", "task_list_id", "completed"]
    search_fields = ['project__name', "name", "task_list_id"]

admin.site.register(Tokens, TokenAdmin)
admin.site.register(Projects, ProjectAdmin)
admin.site.register(Tasks, TaskAdmin)
admin.site.register(SubTasks, SubTaskAdmin)
admin.site.register(ZohoUsers, ZohoUserAdmin)
admin.site.register(TaskList, TaskListAdmin)
admin.site.register(TimeSheet, TimeSheetAdmin)
admin.site.register(Milestone, MilestoneAdmin)