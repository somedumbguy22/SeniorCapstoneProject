from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag
def rating_stars(css_id=None, initial=None, count=None, caption=None):
    if caption:
        caption = caption.strip() + " "
    return render_to_string("internal/rating_stars.html", {"id": css_id or "", "initial": initial, "count": count, "caption": caption})