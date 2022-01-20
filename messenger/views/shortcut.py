import json
import logging

from django.http import HttpRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


logger = logging.getLogger(__name__)


@csrf_exempt
def shortcut_events(request: HttpRequest, *args, **kwargs):
    logger.debug("Shortcut hook received: " + request.body.decode("utf-8"))

    data = json.loads(request.body)

    references: list[dict] = data.get("references", [])
    needs_testing_state_id = None
    for reference in references:
        if reference.get("entity_type") == "workflow-state" and reference.get("name") == "Needs Testing":
            needs_testing_state_id = reference["id"]

    if needs_testing_state_id is None:
        return JsonResponse({})

    actions: list[dict] = data.get("actions", [])
    if len(actions) == 0:
        return JsonResponse({})

    for action in actions:
        if action.get("entity_type") != "story":
            continue

        if "workflow_state_id" not in action.get("changes", {}):
            continue

        workflow_change = action["changes"]["workflow_state_id"]

        if workflow_change["new"] == needs_testing_state_id:
            logger.debug("Ready for testing!")
        else:
            logger.debug("Not ready for testing.")

    return JsonResponse({})
