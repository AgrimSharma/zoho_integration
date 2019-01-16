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

    list_display = ['projects', "task_id", "start_date", "end_date"]


class TimeSheetAdmin(admin.ModelAdmin):
    pass


class MilestoneAdmin(admin.ModelAdmin):
    pass


admin.site.register(Tokens, TokenAdmin)
admin.site.register(Projects, ProjectAdmin)
admin.site.register(Tasks, TaskAdmin)
admin.site.register(ZohoUsers, ZohoUserAdmin)
admin.site.register(TimeSheet, TimeSheetAdmin)
admin.site.register(Milestone, MilestoneAdmin)