import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from remindmoi_bot.models import Reminder
from remindmoi_bot.scheduler import scheduler
from remindmoi_bot.zulip_utils import send_private_zulip


@csrf_exempt
@require_POST
def add_reminder(request):
    # TODO: make it safer. Add CSRF validation. Sanitize/validate post data
    reminder_obj = json.loads(request.body)
    reminder = Reminder(**reminder_obj)
    reminder.save()
    msg = f"Don't forget: {reminder.title}"
    scheduler.add_job(
        send_private_zulip,
        'date',
        run_date=reminder.deadline,
        args=[reminder.zulip_user_email, msg]
    )
    return JsonResponse({'success': True})
