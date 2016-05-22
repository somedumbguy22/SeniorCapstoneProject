from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag
def item_listing(items):
    return render_to_string("internal/item_listing.html", {
        "items": items
    })