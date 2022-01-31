from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.timezone import now

from messenger.models.common import Model


class IterationReport(Model):
    iteration_name = models.CharField(max_length=500)
    iteration_data = models.JSONField(encoder=DjangoJSONEncoder)
    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = "iteration_reports"
