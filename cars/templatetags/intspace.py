from django import template

register = template.Library()


@register.filter
def intspace(value):
    import re

    orig = str(value)

    new = re.sub(r"^(-?\d+)(\d{3})", r"\g<1> \g<2>", orig)
    if orig == new:
        return new
    else:
        return intspace(new)
