# Remind Moi - A Zulip Bot for Scheduling Reminders
## Basic Usage
The bot is composed of two parts: A bot handler `remindmoi_bot_handler.py`, and a Django application that stores and manages reminders. They communciate through Django API-style endpoints. 

(Currently only `/add_reminder/` is implemented.)

## Quick Start
1- Install the requirments either from the `Pipfile` or `requirements.txt`.

2- Download and place your zuliprc file in the root directory of the project.

3- Start the django server `./remindmoi/manage.py runserver`

4- Start the zulip bot handler `zulip-run-bot remindmoi_bot_handler.py --config-file zuliprc`

## Deploying 
TODO
