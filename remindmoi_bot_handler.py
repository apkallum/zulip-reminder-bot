import json
import requests

from typing import Any, Dict

from bot_helpers import (ADD_ENDPOINT, REMOVE_ENDPOINT, LIST_ENDPOINT)
from bot_helpers import (is_valid_add_command,
                         is_valid_remove_command,
                         is_valid_list_command,
                         parse_add_command_content,
                         parse_remove_command_content,
                         parse_reminders_list)


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


handler_class = RemindMoiHandler
