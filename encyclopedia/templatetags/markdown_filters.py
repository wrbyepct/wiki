from django import template
from markdown import markdown

register = template.Library()

# Make this python file loadable in frontend template 
# And call the function as filter 

@register.filter
def markdown_to_html(value):
    return markdown(value)