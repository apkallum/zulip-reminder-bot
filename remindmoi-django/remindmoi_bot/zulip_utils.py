import zulip

from typing import Any

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
    reminder.delete()  # Remove the reminder object upon sending the message
    return response['result'] == 'success'


def create_repeat_reminder(reminder_id: int, repeat_unit: Any) -> None:
    # Create new reminder objects? Change scheduler type to recurring?
    pass
