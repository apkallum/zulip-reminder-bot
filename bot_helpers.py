from typing import Any, Dict
from datetime import timedelta, datetime


UNITS = ["minutes", "hours", "days", "weeks"]
SINGULAR_UNITS = ["minute", "hour", "day", "week"]
REPEAT_UNITS = ["weekly", "daily", "monthly"] + ["minutely"]  # Remove after testing

ENDPOINT_URL = "http://localhost:8789"
ADD_ENDPOINT = ENDPOINT_URL + "/add_reminder"
REMOVE_ENDPOINT = ENDPOINT_URL + "/remove_reminder"
LIST_ENDPOINT = ENDPOINT_URL + "/list_reminders"
REPEAT_ENDPOINT = ENDPOINT_URL + "/repeat_reminder"
MULTI_REMIND_ENDPOINT = ENDPOINT_URL + "/multi_remind"


def is_add_command(content: str, units=UNITS + SINGULAR_UNITS) -> bool:
    """
    Ensure message is in form <COMMAND> reminder <int> UNIT <str>
    """
    try:
        command = content.split(" ", maxsplit=4)  # Ensure the last element is str
        assert command[0] == "add"
        assert type(int(command[1])) == int
        assert command[2] in units
        assert type(command[3]) == str
        return True
    except (IndexError, AssertionError, ValueError):
        return False


def is_remove_command(content: str) -> bool:
    try:
        command = content.split(" ")
        assert command[0] == "remove"
        assert type(int(command[1])) == int
        return True
    except (AssertionError, IndexError, ValueError):
        return False


def is_list_command(content: str) -> bool:
    try:
        command = content.split(" ")
        assert command[0] == "list"
        return True
    except (AssertionError, IndexError, ValueError):
        return False


def is_repeat_reminder_command(content: str, units=UNITS + SINGULAR_UNITS) -> bool:
    try:
        command = content.split(" ")
        assert command[0] == "repeat"
        assert type(int(command[1])) == int
        assert command[2] == "every"
        assert type(int(command[3])) == int
        assert command[4] in units
        return True
    except (AssertionError, IndexError, ValueError):
        return False


def is_multi_remind_command(content: str) -> bool:
    try:
        command = content.split(" ", maxsplit=2)
        assert command[0] == "multiremind"
        assert type(int(command[1])) == int
        return True
    except (AssertionError, IndexError, ValueError):
        return False


def parse_add_command_content(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given a message object with reminder details,
    construct a JSON/dict.
    """
    content = message["content"].split(
        " ", maxsplit=3
    )  # Ensure the last element is str
    return {
        "zulip_user_email": message["sender_email"],
        "title": content[3],
        "created": message["timestamp"],
        "deadline": compute_deadline_timestamp(
            message["timestamp"], content[1], content[2]
        ),
        "active": True,
    }


def parse_remove_command_content(content: str) -> Dict[str, Any]:
    command = content.split(" ")
    return {"reminder_id": command[1]}


def parse_repeat_command_content(content: str) -> Dict[str, Any]:
    command = content.split(" ")
    return {
        "reminder_id": command[1],
        "repeat_unit": command[4],
        "repeat_value": command[3],
    }


def parse_multi_remind_command_content(content: str) -> Dict[str, Any]:
    """
    multiremind 23 @**Jose** @**Max** ->
    {'reminder_id': 23, 'users_to_remind': ['Jose', Max]}
    """
    command = content.split(" ", maxsplit=2)
    users_to_remind = command[2].replace("*", "").replace("@", "").split(" ")
    return {"reminder_id": command[1], "users_to_remind": users_to_remind}


def generate_reminders_list(response: Dict[str, Any]) -> str:
    bot_response = ""
    reminders_list = response["reminders_list"]
    if not reminders_list:
        return "No reminders avaliable."
    for reminder in reminders_list:
        bot_response += f"""
        \nReminder id {reminder['reminder_id']}, titled {reminder['title']}, is scheduled on {datetime.fromtimestamp(reminder['deadline']).strftime('%Y-%m-%d %H:%M')}
        """
    return bot_response


def compute_deadline_timestamp(
    timestamp_submitted: str, time_value: int, time_unit: str
) -> str:
    """
    Given a submitted stamp and an interval,
    return deadline timestamp.
    """
    if time_unit in SINGULAR_UNITS:  # Convert singular units to plural
        time_unit = f"{time_unit}s"

    interval = timedelta(**{time_unit: int(time_value)})
    datetime_submitted = datetime.fromtimestamp(timestamp_submitted)
    return (datetime_submitted + interval).timestamp()
