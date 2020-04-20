from django import template
register = template.Library()

@register.filter
def index(indexable, i):
    return indexable[i]

@register.filter
def index_length(indexable, i):
    return len(indexable[i])