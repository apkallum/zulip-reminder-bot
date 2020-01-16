import zulip

from typing import Any, Dict

from remindmoi.settings import ZULIPRC
from remindmoi_bot.models import Reminder


# Pass the path to your zuliprc file here.
client = zulip.Client(config_file=ZULIPRC)


def send_private_zulip(email: str, msg: str, reminder_id: int) -> bool:
    response = client.send_message({
        "type": "private",
        "to": email,
        "content": msg
    })
    reminder = Reminder.objects.get(reminder_id=reminder_id)
    reminder.active = False  # Remove the reminder object upon sending the message
    return response['result'] == 'success'


def create_repeat_reminder(reminder_id: int, repeat_unit: str) -> None:
    # Create new reminder objects? Change scheduler type to recurring?
    pass


def repeat_unit_to_interval(repeat_unit: str) -> Dict[str, int]:
    if repeat_unit == 'minutely':
        return {'minutes': 1}
    if repeat_unit == 'daily':
        return {'days': 1}
    if repeat_unit == 'weekly':
        return {'weeks': 1}
    if repeat_unit == 'monthly':
        return {'months': 1}
