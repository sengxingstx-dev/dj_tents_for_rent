# core/templatetags/core_tags.py
from django import template

from core.views import get_booking_selection  # Import helper function

register = template.Library()


@register.simple_tag(takes_context=True)
def get_selection_count(context):
    """Returns the total number of items/sets in the booking selection."""
    request = context.get("request")
    if request:
        selection = get_booking_selection(request.session)
        item_count = sum(data["quantity"] for data in selection.get("items", {}).values())
        set_count = sum(data["quantity"] for data in selection.get("sets", {}).values())
        return item_count + set_count
    return 0


@register.simple_tag(takes_context=True)
def get_selection_items(context):
    """Returns detailed items from the booking selection (use carefully)."""
    # This could be used to display a mini-cart, but might be slow.
    # It's generally better to just show the count in the header.
    request = context.get("request")
    if request:
        # Add logic similar to view_booking_selection to fetch item details
        # Be mindful of performance implications here.
        pass
    return []
