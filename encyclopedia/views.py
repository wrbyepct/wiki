from django import forms
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from . import util
import random
from .constant import *

class EntryForm(forms.Form):
    title = forms.CharField(max_length=50, label=False)
    content = forms.CharField(widget=forms.Textarea, required=False, label=False)


def index(request):
    return render(request, INDEX_TEMPLATE, {
        "entries": util.list_entries()
    })


def render_entry(request, entry_title):
    """Handle display, request edit, delete entry
    1. If the request is 'POST': 
        1.If 'delete' is pressed => 1. Delete the entry 2. Redirect to index page.
        2. If 'edit' is pressed => Redirect to edit page with title as argument.
            
    2. If the request is 'GET':
        1.If the entry exists => Display the entry content from markdown to HTML.
        2. If not exists => Display page not found.
    """
    if request.method == "POST":
        # If delete button is clicked, delete it 
        if "delete" in request.POST:
            entry_to_delelte = request.POST.get("delete")
            util.delete_entry(entry_to_delelte)
            return redirect("index")
        else:
            # If "edit" is clicked, redirect to the corresponding page
            to_edit_title = request.POST.get("edit")
            edit_url = reverse("edit") + f"?title={to_edit_title}"
            return redirect(edit_url)

    else:
        entries = [entry.lower() for entry in util.list_entries()]
        
        # Handle entry exists or not
        if entry_title.lower() in entries:
            # If exists render the entry markdown content 
            content_md = util.get_entry(title=entry_title)
            return render(request, ENTRY_TEMPLATE,
                    {"entry_title": entry_title, "content": content_md})
        else:
            # If not then render not found pag
            return render(request, PAGE_NOT_FOUND_TEMPLATE)
    
    
def render_results(request):
    """Checking if query matches the existing entries:
    
    1. If matched => Redirect to that entry
    2. If not => Display any entry contains the query as substring
    
    """
   
    query = request.POST.get("q")
    entries = util.list_entries()
    entries_lower = [entry.lower() for entry in entries]
    
    # Redirect to the entry page if matched exactly
    if query.lower() in entries_lower:
        return redirect(f"/wiki/{query}")
    
    # List results of any entry contains query as substring 
    matched = util.filter_substr(str_list=entries, substr=query)
    return render(request, RESULT_TEMPLATE, {"results": matched})


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
    if request.method == "POST":
        
        entry_form = EntryForm(request.POST)
        
        # Check if the form matches the specification 
        if entry_form.is_valid():
            
            # Extract newly created entry data
            title = entry_form.cleaned_data["title"]
            content = entry_form.cleaned_data["content"]
            
            # Check for existing entries
            entries = [entry.lower() for entry in util.list_entries()]
            if title.lower() in entries:
                # If an entry aready exits, render error message and keep the filled form 
                messages.error(request, 'This entry has already existed')
                return render(request, 
                              NEW_PAGE_TEMPLATE, 
                              {"form": entry_form})
                        
            # If not existed, save to Mardown file
            # And redirect to entry page
            util.save_entry(title=title, content=content)
            messages.success(request, 'New entry saved!')
            return redirect(f"wiki/{title}")
        else:
            return HttpResponse(f"Form is invalid: {entry_form.errors}")
    else:
        # If it's GET method, for render an empty form 
        empty_form = EntryForm()
        return render(request, 
                  NEW_PAGE_TEMPLATE, 
                  {"form": empty_form})
        
        
def render_edit(request):
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
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            original_title = request.POST.get("original_title")
            content = form.cleaned_data["content"]
            new_title = form.cleaned_data["title"]
            util.save_edit(original_title=original_title,
                           new_title=new_title, 
                           content=content)
            
            # Redirect to the entry page 
            messages.success(request, 'Your changes have been saved.')
            return redirect(f"wiki/{new_title}")
        else:
            return HttpResponse(f"Form is invalid: {entry_form.errors}")
    
    
    # If it's GET, render the existing entry as a form
    title = request.GET.get("title", None)
    if title:
        content = util.get_entry(title=title, include_title=False)
        if content is None:
            return render(request, PAGE_NOT_FOUND_TEMPLATE)
        entry_form = EntryForm({"title": title, "content": content})
        return render(request, 
                    EDIT_TEMPLATE, 
                    {"form": entry_form, "title": title} )
    else:
        return render(request, PAGE_NOT_FOUND_TEMPLATE)
    
def render_random(request):
    """Random direct user to an existing entry page"""
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return redirect(f"wiki/{random_entry}")