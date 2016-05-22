from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.filter(is_safe=False)
def multiply(value, arg):
    """Multiplies argument by value"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        try:
            return value * arg
        except Exception:
            return ''


@register.filter(is_safe=False)
def currency(dollars):
    dollars = round(float(dollars), 2)
    return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])