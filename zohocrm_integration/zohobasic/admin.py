# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *


class TokenAdmin(admin.ModelAdmin):
    list_display = ['access_token', "created_at"]


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_id', "name", "status"]


class ZohoUserAdmin(admin.ModelAdmin):
    def task(self, obj):
        return obj.tasks.task_name
    list_display = ['username', "task"]


class TaskAdmin(admin.ModelAdmin):
    raw_id_fields = ['project']

    def projects(self,obj):
        return obj.project.name

    list_display = ['projects', "task_id", "milestone_id", "start_date", "end_date"]
    search_fields = ['project__name',"milestone_id"]


class TimeSheetAdmin(admin.ModelAdmin):
    raw_id_fields = ['project']

    def projects(self, obj):
        return obj.project.name

    def tasks(self, obj):
        return obj.task.task_name
    list_display = ['projects', "tasks", "owner_name", "total_minutes"]
    search_fields = ['project__name']


class MilestoneAdmin(admin.ModelAdmin):
    raw_id_fields = ['project']

    def projects(self, obj):
        return obj.project.name

    list_display = ['projects', "name", "start_date", "end_date"]
    search_fields = ['project__name']


admin.site.register(Tokens, TokenAdmin)
admin.site.register(Projects, ProjectAdmin)
admin.site.register(Tasks, TaskAdmin)
admin.site.register(ZohoUsers, ZohoUserAdmin)
admin.site.register(TimeSheet, TimeSheetAdmin)
admin.site.register(Milestone, MilestoneAdmin)