from django import template

register = template.Library()


@register.filter(name="dot_thousands")
def dot_thousands(value):
    try:
        # cast to float then to int to drop decimals, ensure numbers and strings work
        num = int(float(value))
    except (ValueError, TypeError):
        return value
    # format with commas and swap to dots for thousands
    return f"{num:,}".replace(",", ".")

