import logging

from slack_bolt import App

from core import env

logger = logging.getLogger(__name__)

app = App(
    token=env.get_str("SLACK_BOT_TOKEN"),
    signing_secret=env.get_str("SLACK_SIGNING_SECRET"),
    # disable eagerly verifying the given SLACK_BOT_TOKEN value
    token_verification_enabled=False,
)
