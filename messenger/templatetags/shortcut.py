from datetime import datetime
from django import template
from django.utils import dateparse

register = template.Library()


@register.filter(name="datetimestr")
def datetime_str(s: str) -> datetime | None:
    """Returns a datetime from the string."""
    return dateparse.parse_datetime(s)
