def task_project(request, project_id):
    token = Tokens.objects.get(id=1)
    project = Projects.objects.get(project_id=project_id)
    access_token = token.access_token
    # url = "https://projectsapi.zoho.com/restapi/portal/{portal_id}/" \
    #       "projects/{project_id}/tasks/".format(project_id=project_id,
    #                                             portal_id=settings.PORTAL_ID)
    url = project.task_url
    headers = {
        'authorization': "Bearer {}".format(access_token),
    }

    response = requests.request("GET", url, headers=headers)
    data = response.json()
    response = []
    if data:
        data = data['tasks']
    for d in data:
        try:
            task = Tasks.objects.get(task_id=d['id'])
        except Exception:
            project = Projects.objects.get(project_id=project_id)
            ta = Tasks.objects.create(task_id=d.get('id',""), project=project)
            task = Tasks.objects.get(task_id=d['id'])

        try:
            # details = d.get('details',"")
            own = ZohoUsers.obejcts.filter(tasks=task)
            print own
            owner = [dict(name=o.username, id=o.user_id) for o in own]

        except Exception:
            details = d.get('details',"")
            owner = []
            for o in details['owners']:
                if o['name'] != 'Unassigned':
                    owner.append(dict(name=o['name'], id=o['id']))
                    o = ZohoUsers.objects.create(tasks=task, user_id=o['id'], username=o['name'])
                    o.save()

        timesheet=d['link']['timesheet']['url']
        self_url=d['link']['self']['url']

        try:
            status = d['status']['name']
            color_code=d['status']['color_code']
        except Exception:
            status = None
            color_code=None
        try:
            completed_time=d['completed_time']
        except Exception:
            completed_time=None
        try:
            percent_complete=d['percent_complete']
            percent_complete = percent_complete
        except Exception:
            percent_complete=0
        try:
            description = d['description']
        except Exception:
            description = None
        try:
            end_date=d['end_date']
        except Exception:
            end_date = ""
        try:
            start_date=d['start_date']
        except Exception:
            start_date = ""

        task.milestone_id=d['milestone_id']
        task.self_url=self_url
        task.timesheet_url=timesheet
        task.description=description
        task.duration=d['duration']
        task.task_id=d['id']
        task.task_key=d['key']
        task.created_person = d['created_person']
        task.created_time = d['created_time']
        task.subtasks=d['subtasks']
        task.work=d['work']
        task.completed=d['completed']
        task.percent_complete=percent_complete
        task.last_updated_time=d['last_updated_time']
        task.completed_time=completed_time
        task.task_name=d['name']
        task.tasklist_id = d['tasklist']['id']
        task.status=status
        task.color_code=color_code
        task.end_date=end_date
        task.start_date=start_date


        task.save()
        resp = dict(
            end_date=task.end_date,
            milestone_id=task.milestone_id,
            duration=task.duration,
            task_id=task.task_id,
            start_date=start_date,
            subtasks=task.subtasks,
            task_name=task.task_name,
            description=task.description,
            timesheet=task.timesheet_url,
            owners=owner,
            created_person=task.created_person,
            created_time=task.created_time,
            completed=task.completed,
            percent_complete=task.percent_complete + "%",
            completed_time=task.completed_time,
            status=task.status
        )
        response.append(resp)
    return render(request, 'tasks.html', {"tasks": response})


