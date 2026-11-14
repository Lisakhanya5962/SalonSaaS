
from django import template


register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Safely get a value from a dictionary using a template key.
    """

    if dictionary is None:
        return None

    return dictionary.get(key)
