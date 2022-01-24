from datetime import datetime

from django.utils import dateparse

from core import env
from messenger.shortcut import ShortcutClient


class IterationNotFound(Exception):
    def __init__(self, name: str):
        self.name = name


def _filter_high_comment_stories(stories: list[dict]) -> dict[str, int]:
    return {story["id"]: len(story.get("comments", [])) for story in stories if len(story.get("comments", [])) > 8}


def _filter_high_uat_stories(labels: list[dict], stories: list[dict]) -> dict[str, int]:
    uat_not_approved = next((label for label in labels if label["name"] == "UAT: Not Approved"), None)

    if uat_not_approved is None:
        return {}

    matching_stories = {}
    for story in stories:
        matching_events = []
        for h in story.get("history", []):
            for action in h.get("actions", []):
                if "label_ids" not in action.get("changes", {}):
                    continue

                if "adds" not in action["changes"]["label_ids"]:
                    continue

                added_labels = action["changes"]["label_ids"]["adds"]

                if uat_not_approved["id"] in added_labels:
                    matching_events.append(h)
        if len(matching_events) > 2:
            matching_stories[story["id"]] = len(matching_events)

    return matching_stories


def _filter_uat_rejected_stories(labels: list[dict], stories: list[dict]) -> list[str]:
    uat_not_approved = next((label for label in labels if label["name"] == "UAT: Not Approved"), None)

    if uat_not_approved is None:
        return []

    matching_stories = []
    for story in stories:
        matched = False
        for h in story.get("history", []):
            if matched:
                break

            for action in h.get("actions", []):
                if "label_ids" not in action.get("changes", {}):
                    continue

                if "adds" not in action["changes"]["label_ids"]:
                    continue

                added_labels = action["changes"]["label_ids"]["adds"]

                if uat_not_approved["id"] in added_labels:
                    matching_stories.append(story["id"])

    return matching_stories


def _filter_added_after_start(
    stories: list[dict],
    start_date: datetime,
    iteration_id: str,
) -> dict[str, str]:
    matching_stories = {}
    for story in stories:
        matched = False
        for h in story.get("history", []):
            if matched:
                break

            changed_at = dateparse.parse_datetime(h["changed_at"])
            if changed_at is None:
                raise RuntimeError(f"Unable to parse change event changed_at {h['changed_at']}")

            for action in h.get("actions", []):
                if "iteration_id" not in action.get("changes", {}):
                    continue

                new_id = action["changes"]["iteration_id"].get("new")

                if iteration_id == new_id and changed_at.date() > start_date.date():
                    matching_stories[story["id"]] = h["changed_at"]
                    matched = True
                    break

    return matching_stories


def _filter_stories_by_team(stories: list[dict]) -> dict[str, list[str]]:
    breakdown: dict[str, list[str]] = {
        "enterprise": [],
        "smb": [],
        "other": [],
    }

    for story in stories:
        notable_labels = [label["name"] for label in story["labels"] if label["name"] in ("CS - ENT", "CS - SMB")]
        if notable_labels:
            if "CS - ENT" in notable_labels:
                breakdown["enterprise"].append(story["id"])
            if "CS - SMB" in notable_labels:
                breakdown["smb"].append(story["id"])
        else:
            breakdown["other"].append(story["id"])

    return breakdown


def _filter_stories_by_state(stories: list[dict]) -> dict[str, list[str]]:
    breakdown: dict[str, list[str]] = {
        "not_started": [],
        "started": [],
        "completed": [],
    }

    for story in stories:
        if story["completed"]:
            breakdown["completed"].append(story["id"])
        elif story["started"]:
            breakdown["started"].append(story["id"])
        else:
            breakdown["not_started"].append(story["id"])

    return breakdown


def get_iteration_report(name: str):
    api_token = env.get_str("SHORTCUT_TOKEN")
    if api_token is None:
        raise ValueError("Missing SHOTRCUT_TOKEN environment variable.")

    c = ShortcutClient(api_token=api_token)

    iteration = c.get_iteration_by_name(name)
    if iteration is None:
        raise IterationNotFound(name)

    start_date = dateparse.parse_datetime(iteration["start_date"])
    if start_date is None:
        raise RuntimeError("Unable to parse iteration start_date")

    slim_stories = c.get_iteration_stories(iteration["id"])

    story_ids = [f"{s.get('id')}" for s in slim_stories]
    stories = c.get_stories(story_ids, with_history=True)

    labels = c.get_labels()

    high_comment_stories = _filter_high_comment_stories(stories)
    high_uat_stories = _filter_high_uat_stories(labels, stories)
    added_after_start = _filter_added_after_start(stories, start_date, iteration["id"])
    rejected_uat_stories = _filter_uat_rejected_stories(labels, stories)
    stories_by_team = _filter_stories_by_team(stories)
    stories_by_state = _filter_stories_by_state(stories)

    # WIP
    # How much work lacked communication

    return {
        "iteration": iteration,
        "stories": {story["id"]: story for story in stories},
        "high_comment_stories": high_comment_stories,
        "high_uat_stories": high_uat_stories,
        "added_after_start": added_after_start,
        "rejected_uat_stories": rejected_uat_stories,
        "stories_by_team": stories_by_team,
        "stories_by_state": stories_by_state,
    }
