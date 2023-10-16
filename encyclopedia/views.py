
from .request_handlers import (
    IndexRequestHandler,
    EntryRequestHandler, 
    ResultRequestHandler, 
    NewPageRequestHandler, 
    EditRequestHandler,
    RandomPageRequestHandler,
)

from .form import EntryForm
from django.shortcuts import render 
from .constant import ERROR_TEMPLATE

def index(request):
    handler = IndexRequestHandler()
    return handler.handle_get(request)


def render_entry(request, entry_title):
    """Handle display, request edit, delete entry
    1. If the request is 'POST': 
        1. If 'delete' is pressed => 1. Delete the entry 2. Redirect to index page.
        2. If 'edit' is pressed => Redirect to edit page with title as argument.
            
    2. If the request is 'GET':
        1. If the entry exists => Display the entry content from markdown to HTML.
        2. If not exists => Display page not found.
    """
    handler = EntryRequestHandler()
    
    if request.method == "GET":
        # If delete button is clicked, delete it 
        return handler.handle_get(request, entry_title)
    
    return handler.handle_post(request, entry_title)
    
    
def render_results(request):
    """Checking if query matches the existing entries:
    
    1. If matched => Redirect to that entry
    2. If not => Display any entry contains the query as substring
    
    """
    handler = ResultRequestHandler()
    
    return handler.handle_get(request)


def render_new_page(request):
    """Handle rendering new_page.html:
    1. POST => 
        1. If the form is valid => 
            1. Save the entry
            2. Redirct to the entry page 
            3. Display success message
            
        2. If not valid => Display error messages
            
    2. GET =>
        Simply render empty form in new_page.html
    """
    if request.method == "GET":
        handler = NewPageRequestHandler()
        return handler.handle_get(request, EntryForm())
    
    handler = NewPageRequestHandler()
    return handler.handle_post(request, EntryForm(request.POST))

        
def render_edit(request, entry_title):
    """Handle edit page rendering:
    1. POST - Collect the submitted data, put them into form and check if it's valid
        1. If valid => 
            1. Save the changes
            2. Display success messaages
            3. Redirect to that entry page
        2. IF NOT valid => 
            Display form not valid error
    
    2. GET - Get the additonal argument title to and return the content as form
        1. If title is in the argurment => return the content as form
        2. If NOT => return page not found
    """
    handler = EditRequestHandler()
    if request.method == "GET":
        return handler.handle_get(request, entry_title)
    
    form = EntryForm(request.POST)
    return handler.handle_post(request, form)
    

def render_random(request):
    """Random direct user to an existing entry page"""
    handler = RandomPageRequestHandler()
    return handler.handle_get(request)


def render_foobar(request, foo, bar):
    print(request.GET)
    return render(request, ERROR_TEMPLATE, 
                  {"status_code": "CS50W", "message": "This is prject 1 wiki!"})