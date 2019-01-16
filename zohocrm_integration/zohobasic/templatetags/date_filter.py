from django import template
import datetime
register = template.Library()


@register.filter(name='date_format')
def date_format(value):
    """Removes all values of arg from the given string"""
    return datetime.datetime.strftime(value, "%d-%m-%Y")


