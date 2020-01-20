
from typing import Any, Dict
from datetime import timedelta, datetime


COMMANDS = ['add', 'remove', 'list', 'repeat']
UNITS = ['minutes', 'hours', 'days', 'weeks']
SINGULAR_UNITS = ['minute', 'hour', 'day', 'week']
REPEAT_UNITS = ['weekly', 'daily', 'monthly'] + ['minutely']  # Remove after testing 

ADD_ENDPOINT = 'http://localhost:8789/add_reminder'
REMOVE_ENDPOINT = 'http://localhost:8789/remove_reminder'
LIST_ENDPOINT = 'http://localhost:8789/list_reminders'
REPEAT_ENDPOINT = 'http://localhost:8789/repeat_reminder'


def is_add_command(content: str, units=UNITS + SINGULAR_UNITS) -> bool:
    """
    Ensure message is in form <COMMAND> reminder <int> UNIT <str>
    """
    try:
        command = content.split(' ', maxsplit=4)  # Ensure the last element is str
        assert command[0] == 'add'
        assert command[1] == 'reminder'
        assert type(int(command[2])) == int
        assert command[3] in units
        assert type(command[4]) == str
        return True
    except (IndexError, AssertionError, ValueError):
        return False


def is_remove_command(content: str) -> bool:
    try:
        command = content.split(' ')
        assert command[0] == 'remove'
        assert command[1] == 'reminder'
        assert type(int(command[2])) == int
        return True
    except (AssertionError, IndexError):
        return False


def is_list_command(content: str) -> bool:
    try:
        command = content.split(' ')
        assert command[0] == 'list'
        assert command[1] == 'reminders'
        return True
    except (AssertionError, IndexError):
        return False


def is_repeat_reminder_command(content: str, units=UNITS + SINGULAR_UNITS) -> bool:
    try:
        command = content.split(' ')
        assert command[0] == 'repeat'
        assert command[1] == 'reminder'
        assert type(int(command[2])) == int
        assert command[3] == 'every'
        assert type(int(command[4])) == int
        assert command[5] in units
        return True
    except (AssertionError, IndexError):
        return False


def parse_add_command_content(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given a message object with reminder details,
    construct a JSON/dict.
    """
    content = message['content'].split(' ', maxsplit=4)  # Ensure the last element is str
    return {"zulip_user_email": message['sender_email'],
            "title": content[4],
            "created": message['timestamp'],
            "deadline": compute_deadline_timestamp(message['timestamp'], content[2], content[3]),
            "active": True}


def parse_remove_command_content(content: str) -> Dict[str, Any]:
    command = content.split(' ')
    return {'reminder_id': command[2]}


def parse_repeat_command_content(content:str) -> Dict[str, Any]:
    command = content.split(' ')
    return {'reminder_id': command[2],
            'repeat_unit': command[5],
            'repeat_value': command[4]}


def parse_reminders_list(response: Dict[str, Any]) -> str:
    bot_response = ''
    reminders_list = response['reminders_list']
    for reminder in reminders_list:
        bot_response += f"""
        \nReminder id {reminder['reminder_id']}, titled {reminder['title']}, is scheduled on {datetime.fromtimestamp(reminder['deadline']).strftime('%Y-%m-%d %H:%M')}
        """
    return bot_response


def compute_deadline_timestamp(timestamp_submitted: str, time_value: int, time_unit: str) -> str:
    """
    Given a submitted stamp and an interval,
    return deadline timestamp.
    """
    if time_unit in SINGULAR_UNITS:  # Convert singular units to plural
        time_unit = f"{time_unit}s"

    interval = timedelta(**{time_unit: int(time_value)})
    datetime_submitted = datetime.fromtimestamp(timestamp_submitted)
    return (datetime_submitted + interval).timestamp()