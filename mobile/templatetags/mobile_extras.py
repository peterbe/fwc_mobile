# python
import re

# django 
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

# app 

# mandatory thing to have for magic to work
register = template.Library()

@register.filter()
@stringfilter
def tellink(value):
    value = value.strip().replace(' ','')
    if value.startswith('07'):
        value = '0044' + value[1:]
    return 'tel:%s' % value

