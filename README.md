# Remind Moi - A Zulip Bot for Scheduling Reminders
## Basic Usage
The bot is composed of two parts: A bot handler `remindmoi_bot_handler.py`, and a Django application that stores and manages reminders. They communciate through Django API-style endpoints. 

The three endpoints are: 

1- `/add_reminder/`

2- `/remove_reminder/`

3- `/list_reminders/`

Those endpoints are **not** meant to be interacted with directly. Instead, the bot speaks to them to store & schedule reminders. Further, they don't implement any kind of authentication or CSRF protection. Please do not expose the Django application to the internet. 

## Quick Start
1- Install the requirments either from the `Pipfile` or `requirements.txt`.

2- Download and place your zuliprc file in the root directory of the project.

3- Start the django server `./remindmoi/manage.py runserver`

4- Start the zulip bot handler `zulip-run-bot remindmoi_bot_handler.py --config-file zuliprc`

## Deploying 
TODO
