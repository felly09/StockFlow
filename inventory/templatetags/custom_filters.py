from django import template  #Django provides a template system

register = template.Library()  #this is registerimg the custom tools

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)