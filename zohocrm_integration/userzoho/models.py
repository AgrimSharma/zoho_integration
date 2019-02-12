# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Tokens(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    access_token = models.TextField(max_length=100, null=True, blank=True)
    code = models.TextField(max_length=100, null=True, blank=True)
    refresh_token = models.TextField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Tokens"
        verbose_name_plural = "Tokens"

    def __unicode__(self):
        return "{} : {}".format(self.access_token, self.created_at)

    def __str__(self):
        return "{} : {}".format(self.access_token, self.created_at)


class Portal(models.Model):
    portal_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Portal"
        verbose_name_plural = "Portal"

    def __unicode__(self):
        return "{}".format(self.portal_id)

    def __str__(self):
        return "{}".format(self.portal_id)


class Projects(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    project_id = models.CharField(max_length=100, unique=True, blank=False, null=False)
    name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100,null=True,blank=True)
    description = models.CharField(max_length=1000,null=True,blank=True)
    task_count_open = models.IntegerField(default=0)
    milestone_count_open = models.IntegerField(default=0)
    task_count_close = models.IntegerField(default=0)
    milestone_count_close = models.IntegerField(default=0)
    status = models.CharField(max_length=100,null=True,blank=True)
    created_date_format = models.DateField(null=True,blank=True)
    start_date_format = models.DateField(null=True,blank=True)
    folder_url = models.URLField(null=True,blank=True)
    milestone_url = models.URLField(null=True,blank=True)
    forum_url = models.URLField(null=True,blank=True)
    document_url = models.URLField(null=True,blank=True)
    status_url = models.URLField(null=True,blank=True)
    event_url = models.URLField(null=True,blank=True)
    task_url = models.URLField(null=True,blank=True)
    bug_url = models.URLField(null=True,blank=True)
    self_url = models.URLField(null=True,blank=True)
    timesheet_url = models.URLField(null=True,blank=True)
    user_url = models.URLField(null=True,blank=True)
    tasklist_url = models.URLField(null=True,blank=True)
    activity_url = models.URLField(null=True,blank=True)
    end_date_format = models.DateField(null=True,blank=True)
    id_bug_enabled = models.CharField(max_length=100, null=True,blank=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Projects"
        verbose_name_plural = "Projects"

    def __unicode__(self):
        return "{} : {} :{} ".format(self.project_id, self.name, self.status)

    def __str__(self):
        return "{} : {} :{} ".format(self.project_id, self.name, self.status)


class Tasks(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    project = models.ForeignKey(to=Projects, on_delete=models.CASCADE)
    milestone_id = models.CharField(max_length=100, blank=False, null=False)
    self_url = models.URLField(null=True, blank=True)
    timesheet_url = models.URLField(null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    duration = models.CharField(max_length=100,null=True,blank=True)
    task_id = models.CharField(max_length=1000, unique=True)
    task_key = models.CharField(max_length=1000, null=True,blank=True)
    created_person = models.CharField(max_length=1000, null=True,blank=True)
    created_time = models.DateField(null=True,blank=True)
    subtasks = models.CharField(max_length=100,null=True,blank=True)
    work = models.CharField(max_length=100,null=True,blank=True)
    completed = models.CharField(max_length=1000,null=True,blank=True)
    percent_complete = models.CharField(max_length=1000,null=True,blank=True)
    last_updated_time = models.DateField(null=True,blank=True)
    task_name = models.CharField(max_length=1000,null=True,blank=True)
    tasklist_id = models.CharField(max_length=1000,null=True,blank=True)
    status = models.CharField(max_length=1000,null=True,blank=True)
    color_code = models.CharField(max_length=1000,null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    start_date = models.DateField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Tasks"
        verbose_name_plural = "Tasks"

    def __unicode__(self):
        return "{} : {} :{} ".format(self.task_id, self.status, self.created_person)

    def __str__(self):
        return "{} : {} :{} ".format(self.task_id, self.status, self.created_person)


class ZohoUsers(models.Model):
    tasks = models.ForeignKey(to=Tasks, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=1000)
    username = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Zoho Users"
        verbose_name_plural = "Zoho Users"

    def __unicode__(self):
        return "{} : {} : {}".format(self.user_id, self.username, self.tasks.task_id)

    def __str__(self):
        return "{} : {} : {}".format(self.user_id, self.username, self.tasks.task_id)


class TimeSheet(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    project = models.ForeignKey(to=Projects, on_delete=models.CASCADE)
    task = models.ForeignKey(to=Tasks, on_delete=models.CASCADE)
    last_modified_date = models.DateField(null=True, blank=True)
    bill_status = models.CharField(max_length=100, null=True, blank=True)
    time_sheet_id = models.CharField(max_length=100, null=True, blank=True)
    owner_name = models.CharField(max_length=100, null=True, blank=True)
    hours = models.CharField(max_length=100, null=True, blank=True)
    total_minutes = models.CharField(max_length=100, null=True, blank=True)
    hours_display = models.CharField(max_length=100, null=True, blank=True)
    notes = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Time Sheet"
        verbose_name_plural = "Time Sheet"

    def __unicode__(self):
        return "{} : {} : {}".format(self.project.name, self.task.task_name,
                                     self.bill_status)

    def __str__(self):
        return "{} : {} : {}".format(self.project.name, self.task.task_name,
                                     self.bill_status)


class Milestone(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    project = models.ForeignKey(to=Projects, on_delete=models.CASCADE)
    owner_name = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    sequence = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    flag = models.CharField(max_length=100, null=True, blank=True)
    id_string = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Milestone"
        verbose_name_plural = "Milestone"

    def __unicode__(self):
        return "{} : {} : {}".format(self.project.name,self.name,self.status )

    def __str__(self):
        return "{} : {} : {}".format(self.project.name, self.name, self.status)


class ZohoAllUsers(models.Model):
    user_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    email = models.EmailField()
    role = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "All Users"
        verbose_name_plural = "All Users"

    def __unicode__(self):
        return "{} : {} : {}".format(self.name,self.status,self.role)

    def __str__(self):
        return "{} : {} : {}".format(self.name,self.status,self.role)


class SubTasks(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    tasks = models.ForeignKey(to=Tasks, on_delete=models.CASCADE, related_name="task_fk")
    sub_task_id = models.CharField(max_length=1000,null=True,blank=True)
    depth = models.CharField(max_length=100, null=True, blank=True)
    end_date = models.DateField(null=True,blank=True)
    priority = models.CharField(max_length=1000, null=True, blank=True)
    percent_complete = models.CharField(max_length=1000, null=True, blank=True)
    duration = models.CharField(max_length=1000, null=True, blank=True)
    name = models.CharField(max_length=100,null=True,blank=True)
    start_date = models.DateField(null=True,blank=True)
    completed = models.CharField(max_length=1000, null=True, blank=True)
    created_person = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Sub Tasks"
        verbose_name_plural = "Sub Tasks"

    def __unicode__(self):
        return "{} : {} :{} ".format(self.sub_task_id, self.completed, self.created_person)

    def __str__(self):
        return "{} : {} :{} ".format(self.sub_task_id, self.completed, self.created_person)


class TaskList(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    project = models.ForeignKey(to=Projects, on_delete=models.CASCADE)
    task_list_id = models.CharField(max_length=1000, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    completed = models.CharField(max_length=1000, null=True, blank=True)
    milestone_id = models.CharField(max_length=1000, null=True, blank=True)
    rolled = models.CharField(max_length=1000, null=True, blank=True)
    sequence = models.CharField(max_length=1000, null=True, blank=True)
    view_type = models.CharField(max_length=1000, null=True, blank=True)
    created_time = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Tasks List"
        verbose_name_plural = "Tasks List"

    def __unicode__(self):
        return "{} : {} :{} ".format(self.project.project_id, self.task_list_id,
                                     self.name)

    def __str__(self):
        return "{} : {} :{} ".format(self.project.project_id, self.task_list_id,
                                     self.name)