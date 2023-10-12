from django import forms
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from . import util


class EntryForm(forms.Form):
    title = forms.CharField(max_length=50, label=False)
    content = forms.CharField(widget=forms.Textarea, required=False, label=False)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def render_entry(request, entry_title):
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
            return render(request, "encyclopedia/entry.html",
                    {"entry_title": entry_title, "content": content_md})
        else:
            # If not then render not found pag
            return render(request, "encyclopedia/page_not_found.html")
    
    
def render_results(request):
   
    query = request.POST.get("q")
    entries = util.list_entries()
    entries_lower = [entry.lower() for entry in entries]
    
    # Redirect to the entry page if matched exactly
    if query.lower() in entries_lower:
        return redirect(f"/wiki/{query}")
    
    # List results if the query matches the entries substring 
    matched = util.filter_substr(str_list=entries, substr=query)
    return render(request, "encyclopedia/result.html", {"results": matched})


def render_new_page(request):
    if request.method == "POST":
        
        entry_form = EntryForm(request.POST)
        
        # Check if the form matches the specification 
        if entry_form.is_valid():
            
            # Extract newly created entry data
            title = entry_form.cleaned_data["title"]
            content = entry_form.cleaned_data["content"]
            print(content)
            
            # Check for existing entries
            entries = [entry.lower() for entry in util.list_entries()]
            if title.lower() in entries:
                # If an entry aready exits, render error message and keep the filled form 
                messages.error(request, 'This entry has already existed')
                return render(request, 
                              "encyclopedia/new_page.html", 
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
                  "encyclopedia/new_page.html", 
                  {"form": empty_form})
        
        
def render_edit(request):
    """Handle edit page rendering
    1. POST - Collect the submitted data, put them into form and check if it's valid
            If valid => 1. Save it as new entry 
                        2. Display success messaages
                        3. Redirect to that entry page
            IF NOT valid => Display form not valid error
    
    2. GET - Get the additonal argument title to and return the content as form
            If title is in the argurment => return the content as form
            If titel it NOT in the arguement => return page not found
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
        content = util.get_entry_without_title(title)
        entry_form = EntryForm({"title": title, "content": content})
        return render(request, 
                    "encyclopedia/edit.html", 
                    {"form": entry_form, "title": title} )
    else:
        return render(request, "encyclopedia/page_not_found.html")