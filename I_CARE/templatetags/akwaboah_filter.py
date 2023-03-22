from django import template

register = template.Library()
from decimal import Decimal

@register.filter
def div(value, args):
    return value/args

@register.filter
def divFILL(value):
    return value*Decimal(0.2)


