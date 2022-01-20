# Shortcut Messenger

Shortcut Messenger is a Django app to enable teams to automatically notify each other of changes in Shortcut that are important
to them. Shortcut does not notify when ticket state is changed or labels are added, and this can be an important part of a
team's communication mechanisms.

## What does it actually do, though?

Right now, nothing!

The application currently provides a webhook endpoint for receiving Shortcut events defined by their
[V1 webhook API](https://shortcut.com/api/webhook/v1), and the application is just logging when notable events are triggered right now.

The next step is to hook these notable events into channels in Slack.

## Supported Events

* Moving a ticket to a state called "Needs Testing"
* Add a label called "UAT: Not Approved" to a ticket

## Feature Roadmap

* [ ] Send messages to Slack channels
* [ ] Allow configuring the events that trigger messages and the channels they go to
* [ ] Allow Slack users to receive messages specific to them

## Local Setup

* Create a virtualenv running Python ^3.10

    `pyenv virtualenv 3.10.1 shortcut-messenger`
* Install poetry

    `pip install poetry`
* Installed project dependencies

    `poetry install`

* Copy the `.env.example` to `.env` and configure the values as needed

    `cp .env.example .env`
* Migrate and run the application like any other Django app!

To test webhook receival locally, [ngrok](https://ngrok.com) can be used.

## Add to Shortcut

To add this as a webhook application in shortcut, go to the integrations settings page in Shortcut, and add the domain for this application pointing to the path `https://yourdomain.dev/shortcut/events`
