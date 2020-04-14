import zulip

from typing import Dict, List

from remindmoi.settings import ZULIPRC
from remindmoi_bot.models import Reminder

SINGULAR_UNITS = ["minute", "hour", "day", "week", "month"]

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file=ZULIPRC)


def send_private_zulip_reminder(reminder_id: int) -> bool:
    reminder = Reminder.objects.get(reminder_id=reminder_id)
    emails = reminder.zulip_user_email.split(",")
    content = f"Don't forget: {reminder.title}. Reminder id: {reminder.reminder_id}"
    for email in emails:
        response = client.send_message(
            {"type": "private", "to": email, "content": content}
        )
    reminder.active = (
        False  # For now, set reminder to negative to denoate that it's done
    )
    return response["result"] == "success"


def repeat_unit_to_interval(repeat_unit: str, repeat_value: int) -> Dict[str, int]:
    if repeat_unit in SINGULAR_UNITS:  # Convert singular units to plural
        repeat_unit = f"{repeat_unit}s"

    if repeat_unit == "minutes":
        return {"minutes": int(repeat_value)}
    if repeat_unit == "days":
        return {"days": int(repeat_value)}
    if repeat_unit == "weeks":
        return {"weeks": int(repeat_value)}
    if repeat_unit == "months":
        return {"months": int(repeat_value)}


def get_user_emails(usernames: List[str]) -> List[str]:
    members = client.get_members()["members"]
    user_emails = [
        member["email"] for member in members if member["full_name"] in usernames
    ]
    return user_emails
