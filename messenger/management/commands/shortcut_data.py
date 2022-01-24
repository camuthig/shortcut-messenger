from django.core.management import BaseCommand
from django.core.management.base import CommandParser
from django.utils import timezone


from messenger.shortcut_reporting import get_iteration_report


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser):
        parser.add_argument("name", type=str)

    def handle(self, *args, **options):

        stats = get_iteration_report(options["name"])

        print(f"Iteration: {stats['iteration']['name']}")
        print(f"Start Date: {stats['iteration']['start_date']}")
        print(f"End Date: {stats['iteration']['end_date']}")
        print(f"Report generated at: {timezone.now()}")

        print("High comment stories")
        for story_id, cnt in stats["high_comment_stories"].items():
            story = stats["stories"][story_id]
            print(f"SC-{story['id']} - {story['app_url']}: {cnt}")

        print("")
        print("High Rejections")
        for story_id, cnt in stats["high_uat_stories"].items():
            story = stats["stories"][story_id]
            print(f"SC-{story['id']} - {story['app_url']}: {cnt}")

        print("")
        print("UAT Rejected at Some Point")
        for story_id in stats["rejected_uat_stories"]:
            story = stats["stories"][story_id]
            print(f"SC-{story['id']} - {story['app_url']}")

        print("")
        print("Added after start")
        for story_id, changed_at in stats["added_after_start"].items():
            story = stats["stories"][story_id]
            print(f"SC-{story['id']} - {story['app_url']}: {changed_at}")

        print("")
        print("Number of Tickets by Team")
        print(f"CS-ENT: {len(stats['stories_by_team']['enterprise'])}")
        print(f"CS-SMB: {len(stats['stories_by_team']['smb'])}")
        print(f"Other: {len(stats['stories_by_team']['other'])}")

        print("")
        print("Number of Points by Team")
        ent_points = sum([stats["stories"][id]["estimate"] or 0 for id in stats["stories_by_team"]["enterprise"]])
        print(f"CS-ENT: {ent_points}")
        smb_points = sum([stats["stories"][id]["estimate"] or 0 for id in stats["stories_by_team"]["smb"]])
        print(f"CS-SMB: {smb_points}")
        other_points = sum([stats["stories"][id]["estimate"] or 0 for id in stats["stories_by_team"]["other"]])
        print(f"Other: {other_points}")

        print("")
        print("Number of Tickets by State")
        print(f"Not Started: {len(stats['stories_by_state']['not_started'])}")
        print(f"Started: {len(stats['stories_by_state']['started'])}")
        print(f"Completed: {len(stats['stories_by_state']['completed'])}")

        print("")
        print("Number of Points by State")
        not_started_points = sum(
            [stats["stories"][id]["estimate"] or 0 for id in stats["stories_by_state"]["not_started"]]
        )
        print(f"Not Started: {not_started_points}")
        started_points = sum([stats["stories"][id]["estimate"] or 0 for id in stats["stories_by_state"]["started"]])
        print(f"Started: {started_points}")
        completed_points = sum(
            [stats["stories"][id]["estimate"] or 0 for id in stats["stories_by_state"]["completed"]]
        )
        print(f"Completed: {completed_points}")
