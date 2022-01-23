# Shortcut Messenger

Shortcut Messenger is a Django app to enable teams to automatically notify each other of changes in Shortcut that are important
to them. Shortcut does not notify when ticket state is changed or labels are added, and this can be an important part of a
team's communication mechanisms.

## What does it actually do, though?

The application currently provides a webhook endpoint for receiving Shortcut events defined by their
[V1 webhook API](https://shortcut.com/api/webhook/v1). These events are parsed for specific use cases and used
to send messages to particular channels in Slack.

## Supported Events

* Moving a ticket to a state called "Needs Testing"
* Add a label called "UAT: Not Approved" to a ticket

## Feature Roadmap

* [x] Send messages to Slack channels
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

## Deploy to Cloud Run

### Build and Deploy

The project is designed to be be deployed and run using GCP Cloud Run. To build/deploy in this way, configure your `gcloud` CLI tool
and run

`gcloud run deploy service-name --source .`

### Configure Secrets and Variables

* Add the domain created by GCP for you servcie to an environment variable as `ALLOWED_HOSTS=["<domain>"]`
* Add the following secrets to the GCP Secret Manager and link them to the deployed service
    * SECRET_KEY - your Django application secret key
    * SLACK_SIGNING_KEY - your Slack app's signing key
    * SLACK_BOT_TOKEN - your Slack bot's auth token
    * SHORTCUT_SECRET - The signing secret provied to Shortcut

## Add to Shortcut

To add this as a webhook application in shortcut, go to the integrations settings page in Shortcut, and add the domain for this application pointing to the path `https://yourdomain.dev/shortcut/events`
