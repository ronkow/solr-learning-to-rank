from django import template

register = template.Library()

@register.filter(name='blankspace')

def tag_blankspace(value):
    return value.replace("*","_____")