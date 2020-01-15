import json
import requests

from typing import Any, Dict
from datetime import timedelta, datetime

USAGE = '''
A bot that schedules reminders for users.
To store a reminder, mention or send a message to me in the following format:

<COMMAND> reminder <int> UNIT <title of reminder>

add reminder 1 day clean the dishes
add reminder 10 hours eat

Avaliable time units: minutes, hours, days, weeks

To remove a reminder:
remove reminder <reminder_id>

To list reminders: 
list reminders
'''


COMMANDS = ['add', 'remove', 'list']
UNITS = ['minutes', 'hours', 'days', 'weeks']
SINGULAR_UNITS = ['minute', 'hour', 'day', 'week']

ADD_ENDPOINT = 'http://localhost:8000/add_reminder/'
REMOVE_ENDPOINT = 'http://localhost:8000/remove_reminder'
LIST_ENDPOINT = 'http://localhost:8000/list_reminders'


class RemindMoiHandler(object):
    '''
    A docstring documenting this bot.
    the reminder bot reminds people of its reminders
    '''

    def usage(self) -> str:
        return USAGE

    def handle_message(self, message: Dict[str, Any], bot_handler: Any) -> None:
        bot_response = get_bot_response(message, bot_handler)
        bot_handler.send_reply(message, bot_response)


def get_bot_response(message: Dict[str, Any], bot_handler: Any) -> str:
    if message['content'].startswith(('help', '?')):
        return USAGE

    if is_valid_add_command(message['content']):
        try:
            reminder_object = parse_add_command_content(message)
            response = requests.post(url=ADD_ENDPOINT, json=reminder_object)  # TODO: Catch error when django server is down
            response = response.json()
            assert response['success']
        except (json.JSONDecodeError, AssertionError):
            return "Something went wrong"
        except OverflowError:
            return "What's wrong with you?"
        return f"Reminder stored. Your reminder id is: {response['reminder_id']}"
    if is_valid_remove_command(message['content']):
        try:
            reminder_id = parse_remove_command_content(message['content'])
            response = requests.post(url=REMOVE_ENDPOINT, json=reminder_id)
            response = response.json()
            assert response['success']
        except (json.JSONDecodeError, AssertionError):
            return "Something went wrong"
        return "Reminder deleted."
    if is_valid_list_command(message['content']):
        try:
            zulip_user_email = {'zulip_user_email': message["sender_email"]}
            response = requests.post(url=LIST_ENDPOINT, json=zulip_user_email)
            response = response.json()
            assert response['success']
        except (json.JSONDecodeError, AssertionError):
            return "Something went wrong"
        return parse_reminders_list(response)
    else:
        return "Invlaid input. Please check help."


def is_valid_add_command(content: str, units=UNITS + SINGULAR_UNITS) -> bool:
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


def is_valid_remove_command(content: str) -> bool:
    try:
        command = content.split(' ')
        assert command[0] == 'remove'
        assert command[1] == 'reminder'
        assert type(int(command[2])) == int
        return True
    except (AssertionError, IndexError):
        return False


def is_valid_list_command(content: str) -> bool:
    try:
        command = content.split(' ')
        assert command[0] == 'list'
        assert command[1] == 'reminders'
        return True
    except (AssertionError, IndexError):
        return False


def parse_add_command_content(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given a message object with reminder details,
    construct a JSON/dict.
    """
    content = message['content'].split(' ', maxsplit=4)  # Ensure the last element is str
    return {
        "zulip_user_email": message['sender_email'],
        "title": content[4],
        "created": message['timestamp'],
        "deadline": compute_deadline_timestamp(message['timestamp'], content[2], content[3]),
        "active": True
    }


def parse_remove_command_content(content: str) -> Dict[str, Any]:
    command = content.split(' ')
    return {'reminder_id': command[2]}


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


handler_class = RemindMoiHandler
