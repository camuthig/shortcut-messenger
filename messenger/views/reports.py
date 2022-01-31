from typing import Any
import logging

from django import forms
from django.urls import reverse

from core import env
from messenger import models
from messenger.shortcut import ShortcutClient
from messenger.shortcut_reporting import build_iteration_report_data
from messenger.views.common import CreateView
from messenger.views.common import DetailView
from messenger.views.common import ListView


logger = logging.getLogger(__name__)


class IterationReportListView(ListView):
    template_name = "iteration_reports/list.html"
    model = models.IterationReport


class IterationReportCreateView(CreateView):
    class CreateForm(forms.ModelForm):
        class Meta:
            model = models.IterationReport
            fields = ["iteration_name"]

    template_name = "iteration_reports/create.html"
    form_class = CreateForm
    model = models.IterationReport

    def get_success_url(self) -> str:
        return reverse("iteration-reports-list")

    def handle_form(self, form: CreateForm):
        iteration_name = form.cleaned_data.get("iteration_name")

        logger.info(iteration_name)

        api_token = env.get_str("SHORTCUT_TOKEN")
        if api_token is None:
            raise ValueError("Missing SHOTRCUT_TOKEN environment variable.")

        c = ShortcutClient(api_token=api_token)
        iteration = c.get_iteration_by_name(iteration_name)

        if iteration is None:
            raise forms.ValidationError({"iteration_name": ["Could not find the iteration in Shortcut."]})

        slim_stories = c.get_iteration_stories(iteration["id"])

        story_ids = [f"{s.get('id')}" for s in slim_stories]
        stories = c.get_stories(story_ids, with_history=True)

        labels = c.get_labels()

        iteration_data = {
            "iteration": iteration,
            "stories": stories,
            "labels": labels,
        }

        return models.IterationReport.objects.create(
            iteration_name=iteration_name,
            iteration_data=iteration_data,
        )


class IterationReportView(DetailView):
    object: models.IterationReport
    template_name = "iteration_reports/show.html"
    model = models.IterationReport

    def _points_by_team(self, report_data: dict) -> dict[str, int]:
        ent_points = sum([report_data["stories"][id]["estimate"] or 0 for id in report_data["stories_by_team"]["ent"]])
        smb_points = sum([report_data["stories"][id]["estimate"] or 0 for id in report_data["stories_by_team"]["smb"]])
        other_points = sum(
            [report_data["stories"][id]["estimate"] or 0 for id in report_data["stories_by_team"]["other"]]
        )

        return {
            "ent": ent_points,
            "smb": smb_points,
            "other": other_points,
        }

    def _points_by_state(self, report_data: dict) -> dict[str, int]:
        not_started_points = sum(
            [report_data["stories"][id]["estimate"] or 0 for id in report_data["stories_by_state"]["not_started"]]
        )
        started_points = sum(
            [report_data["stories"][id]["estimate"] or 0 for id in report_data["stories_by_state"]["started"]]
        )
        completed_points = sum(
            [report_data["stories"][id]["estimate"] or 0 for id in report_data["stories_by_state"]["completed"]]
        )

        return {
            "not_started": not_started_points,
            "started": started_points,
            "completed": completed_points,
        }

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context_data = super().get_context_data(**kwargs)

        report_data = build_iteration_report_data(self.object)
        context_data.update(report_data)

        total_stories = len(report_data["stories"])
        total_points = sum([s["estimate"] or 0 for s in report_data["stories"].values()])
        points_by_team = self._points_by_team(report_data)
        points_by_state = self._points_by_state(report_data)
        percent_stories_by_team = {
            k: round((len(s) / total_stories) * 100) for k, s in report_data["stories_by_team"].items()
        }
        percent_stories_by_state = {
            k: round((len(s) / total_stories) * 100) for k, s in report_data["stories_by_state"].items()
        }
        percent_points_by_team = {k: round((p / total_points) * 100) for k, p in points_by_team.items()}
        percent_points_by_state = {k: round((p / total_points) * 100) for k, p in points_by_state.items()}

        context_data["high_uat_stories"] = {
            k: v for k, v in sorted(context_data["high_uat_stories"].items(), key=lambda x: x[1], reverse=True)
        }
        context_data["high_comment_stories"] = {
            k: v for k, v in sorted(context_data["high_comment_stories"].items(), key=lambda x: x[1], reverse=True)
        }
        context_data["added_after_start"] = {
            k: v for k, v in sorted(context_data["added_after_start"].items(), key=lambda x: x[1], reverse=True)
        }
        print(context_data["high_comment_stories"])

        context_data.update(
            {
                "total_points": total_points,
                "total_stories": total_stories,
                "points_by_team": points_by_team,
                "points_by_state": points_by_state,
                "percent_stories_by_team": percent_stories_by_team,
                "percent_points_by_team": percent_points_by_team,
                "percent_stories_by_state": percent_stories_by_state,
                "percent_points_by_state": percent_points_by_state,
            }
        )

        return context_data
