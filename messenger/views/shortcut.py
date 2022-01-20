import json
import logging

from django.http import HttpRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


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
    else:
        logger.debug("Not ready for testing.")


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


@csrf_exempt
def shortcut_events(request: HttpRequest, *args, **kwargs):
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
