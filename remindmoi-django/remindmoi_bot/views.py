import json
import pytz
from apscheduler.jobstores.base import JobLookupError

from datetime import datetime

from dateutil.tz import gettz
from dateutil.parser import *

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from remindmoi_bot.models import Reminder
from remindmoi_bot.scheduler import scheduler
from remindmoi_bot.zulip_utils import (send_private_zulip_reminder,
                                       repeat_unit_to_interval,
                                       get_user_emails)
from apscheduler.triggers.interval import IntervalTrigger

@csrf_exempt
@require_POST
def add_reminder(request):
    # TODO: make it safer. Add CSRF validation. Sanitize/validate post data
    reminder_obj = json.loads(request.body)  # Create and save remninder object
    reminder = Reminder.objects.create(
                               zulip_user_email=reminder_obj['zulip_user_email'],
                               title=reminder_obj['title'],
                               created=datetime.utcfromtimestamp(reminder_obj['created']).replace(tzinfo=pytz.utc),
                               deadline=datetime.utcfromtimestamp(reminder_obj['deadline']).replace(tzinfo=pytz.utc)
                               )
    reminder.save()
    scheduler.add_job(  # Schedule reminder
        send_private_zulip_reminder,
        'date',
        run_date=reminder.deadline,
        args=[reminder.reminder_id],
        # Create job name from title and reminder id
        id=(str(reminder.reminder_id)+reminder.title)
    )
    return JsonResponse({'success': True,
                         'reminder_id': reminder.reminder_id})


def isoadd_reminder(request):
    reminder_obj = json.loads(request.body)  # Create and save remninder object
    reminder = Reminder.objects.create(
                               zulip_user_email=reminder_obj['zulip_user_email'],
                               title=reminder_obj['title'],
                               created=datetime.utcfromtimestamp(reminder_obj['created']).replace(tzinfo=pytz.utc),
                               deadline=datetime.utcfromtimestamp(reminder_obj['deadline']).replace(tzinfo=pytz.utc)
                               )
    reminder.save()
    scheduler.add_job(  # Schedule reminder
        send_private_zulip_reminder,
        'date',
        run_date=reminder.deadline,
        args=[reminder.reminder_id],
        # Create job name from title and reminder id
        id=(str(reminder.reminder_id)+reminder.title)
    )
    return JsonResponse({'success': True,
                         'reminder_id': reminder.reminder_id})


@csrf_exempt
@require_POST
def multi_remind(request):
    """
    Get reminder object and modify the zulip_sender email to
    add emails of other users, comma seperated.
    """
    multi_remind_request = json.loads(request.body)
    reminder_id = multi_remind_request['reminder_id']
    users_list = multi_remind_request['users_to_remind']
    reminder = Reminder.objects.get(reminder_id=int(reminder_id))
    user_emails_to_remind = get_user_emails(users_list) + [reminder.zulip_user_email]
    reminder.zulip_user_email = ','.join(user_emails_to_remind)
    reminder.save()
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def remove_reminder(request):
    reminder_id = json.loads(request.body)['reminder_id']
    reminder = Reminder.objects.get(reminder_id=int(reminder_id))
    try:
        scheduler.remove_job((str(reminder.reminder_id) + reminder.title))  # Remove reminder job
    except JobLookupError:
        """
        Ignore failed job lookups here.
        One-time reminders don't have one after they've fired.
        """
        pass
    reminder.delete()  # Remove reminder object
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def list_reminders(request):
    response_reminders = []  # List of reminders to be returned to the client
    
    zulip_user_email = json.loads(request.body)['zulip_user_email']
    user_reminders = Reminder.objects.filter(zulip_user_email__icontains=zulip_user_email)
    # Return title and deadline (in unix timestamp) of reminders
    for reminder in user_reminders.values():
        job_id = str(reminder['reminder_id']) + reminder['title']
        scheduled_job =  scheduler.get_job(job_id) 
        interval = ''
        if scheduled_job is not None:  
            if isinstance(scheduled_job.trigger,IntervalTrigger):
                interval = f"schedule interval {str(scheduled_job.trigger.interval)}"

        response_reminders.append({'title': reminder['title'],
                                   'deadline': reminder['deadline'].timestamp(),
                                   'reminder_id': reminder['reminder_id'],
                                   'interval' : interval})

    return JsonResponse({'success': True, 'reminders_list': response_reminders})


@csrf_exempt
@require_POST
def repeat_reminder(request):
    repeat_request = json.loads(request.body)
    reminder_id = repeat_request['reminder_id']
    repeat_unit = repeat_request['repeat_unit']
    repeat_value = repeat_request['repeat_value']
    reminder = Reminder.objects.get(reminder_id=reminder_id)
    job_id = (str(reminder.reminder_id)+reminder.title)
    # import ipdb; ipdb.set_trace()
    if scheduler.get_job(job_id) is not None:
        # job exists, modify it
        updated_trigger = scheduler._create_trigger(
            'interval', repeat_unit_to_interval(repeat_unit, repeat_value)
        )
        scheduler.modify_job(job_id, None, trigger=updated_trigger)
    else:
        # job does not exist, create it
        scheduler.add_job(
            send_private_zulip_reminder,
            'interval',
            **repeat_unit_to_interval(repeat_unit, repeat_value),
            args=[reminder.reminder_id],
            id=job_id
        )
    return JsonResponse({'success': True})
