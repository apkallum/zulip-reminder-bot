# Remind Moi - A Zulip Bot for Scheduling Reminders
## Basic Usage

A bot that schedules reminders for users.

To store a reminder, mention or send a message to the bot in the following format:

`add reminder int <UNIT> <title_of_reminder>`

`add reminder 1 day clean the dishes`
`add reminder 10 hours eat`

Avaliable time units: minutes, hours, days, weeks

To remove a reminder:
`remove reminder <reminder_id>`

To list reminders:
`list reminders`

To repeat a reminder: 
repeat reminder <reminder_id> every <int> <time_unit>

`repeat reminder 23 every 2 weeks`

Avaliable units: days, weeks, months

## Quick Start
1- Install the requirments either from the `Pipfile` or `requirements.txt`.

2- Download and place your zuliprc file in the root directory of the project.

3- Start the django server `./remindmoi-django/manage.py runserver 0.0.0.0:8789`

4- Start the zulip bot handler `zulip-run-bot remindmoi_bot_handler.py --config-file etc/zuliprc`

## Usage

The bot is composed of two parts: A bot handler `remindmoi_bot_handler.py`, and a Django application that stores and manages reminders. They communciate through Django API-style endpoints.

Current API endpoints are: 

1- `/add_reminder`

2- `/remove_reminder`

3- `/list_reminders`

4- `/repeat_reminder`

Those endpoints are **not** meant to be interacted with directly. Instead, the bot speaks to them to store & schedule reminders. Further, they don't implement any kind of authentication or CSRF protection. Please do not expose the Django application to the internet. 

## Deploying 

You can deploy the bot however you like. The easisest way is to use `zulip-run-bot` and `manage.py` in a screen or tmux session. However, this solution doesn't provide the ability to manage or restart the bot in case of failures. 

However, we also provide a `supervisor.conf` file to manage the bot's process. The `supervisor.conf` file assumes that the directory to this repo is `/opt/zulip-reminder-bot`. After adding it to your `/etc/supervisor/conf.d`, start the bot using `supervisor start remindmoi-bot:`.
