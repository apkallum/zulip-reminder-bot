import zulip

from typing import Dict

from remindmoi.settings import ZULIPRC
from remindmoi_bot.models import Reminder

SINGULAR_UNITS = ['minute', 'hour', 'day', 'week', 'month']

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


def repeat_unit_to_interval(repeat_unit: str, repeat_value: int) -> Dict[str, int]:
    if repeat_unit in SINGULAR_UNITS:  # Convert singular units to plural
        repeat_unit = f"{repeat_unit}s"

    if repeat_unit == 'minutes':
        return {'minutes': int(repeat_value)}
    if repeat_unit == 'days':
        return {'days': int(repeat_value)}
    if repeat_unit == 'weeks':
        return {'weeks': int(repeat_value)}
    if repeat_unit == 'months':
        return {'months': int(repeat_value)}
