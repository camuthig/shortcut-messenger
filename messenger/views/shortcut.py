import hashlib
import hmac
import json
import logging

from django.http import HttpRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core import env
from messenger import slack


logger = logging.getLogger(__name__)


def _get_testing_state_ref(references: list[dict]) -> dict | None:
    for reference in references:
        if reference.get("entity_type") == "workflow-state" and reference.get("name") == "Needs Testing":
            return reference

    return None


def _get_uat_not_approved_ref(references: list[dict]) -> dict | None:
    for reference in references:
        if reference.get("entity_type") == "label" and reference.get("name") == "UAT: Not Approved":
            return reference

    return None


def _handle_needs_testing(action: dict, needs_testing_state: dict | None):
    if needs_testing_state is None:
        return

    if action.get("entity_type") != "story":
        return

    if "workflow_state_id" not in action.get("changes", {}):
        return

    workflow_change = action["changes"]["workflow_state_id"]

    if workflow_change["new"] == needs_testing_state["id"]:
        logger.debug("Ready for testing!")
        slack.app.client.chat_postMessage(
            channel="shortcut-needs-testing",
            text=f"SC-{action['id']} has been moved to Needs Testing.\n<{action['app_url']}|{action['name']}>",
        )


def _handle_uat_not_approved(action: dict, uat_not_approved_label: dict | None):
    if uat_not_approved_label is None:
        return

    if action.get("entity_type") != "story":
        return

    if "label_ids" not in action.get("changes", {}):
        return

    if "adds" not in action["changes"]["label_ids"]:
        return

    added_labels = action["changes"]["label_ids"]["adds"]

    if uat_not_approved_label["id"] in added_labels:
        logger.debug("UAT was not approved.")
        slack.app.client.chat_postMessage(
            channel="shortcut-uat-not-approved",
            text=f"SC-{action['id']} has been marked UAT: Not Approved.\n<{action['app_url']}|{action['name']}>",
        )


def _check_signature(request: HttpRequest) -> JsonResponse | None:
    shortcut_secret = str(env.get("SHORTCUT_SECRET"))
    signature = str(request.headers.get("Payload-Signature"))
    if not shortcut_secret and not signature:
        return None
    elif shortcut_secret and not signature:
        logger.warning("The application has configured a Shortcut secret, but Shortcut is not sending a signature")
    elif not shortcut_secret and signature:
        logger.warning("The application has not configured a Shortcut secret, but Shortcut is sending a signature")

    computed_signature = hmac.new(bytes(shortcut_secret, "utf-8"), request.body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_signature, signature):
        response = JsonResponse({})
        response.status_code = 401
        return response

    return None


@csrf_exempt
def shortcut_events(request: HttpRequest, *args, **kwargs):
    error_response = _check_signature(request)
    if error_response is not None:
        return error_response

    logger.debug("Shortcut hook received: " + request.body.decode("utf-8"))

    data = json.loads(request.body)

    references: list[dict] = data.get("references", [])
    needs_testing_state = _get_testing_state_ref(references)
    uat_not_approved_label = _get_uat_not_approved_ref(references)

    actions: list[dict] = data.get("actions", [])
    if len(actions) == 0:
        return JsonResponse({})

    for action in actions:
        _handle_needs_testing(action, needs_testing_state)
        _handle_uat_not_approved(action, uat_not_approved_label)

    return JsonResponse({})
