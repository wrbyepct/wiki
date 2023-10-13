
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

import random
from abc import ABC, abstractmethod

from . import util
from .constant import *
from .form import EntryForm
from .service import EntryService
from .dao import EntryDao

class GetRequestHandler(ABC):
    def __init__(self, entry_service=None):
        self.entry_service = entry_service or EntryService(EntryDao)
        
    @abstractmethod
    def handle_get(self, request):
        pass

class GeneralRequestHandler(GetRequestHandler):
        
    @abstractmethod
    def handle_post(self, request):
        pass

class IndexRequestHandler(GetRequestHandler):
    
    def handle_get(self, request):
        return render(request, INDEX_TEMPLATE, {
        "entries": self.entry_service.list_all_entries()
    })


class EntryRequestHandler(GeneralRequestHandler):
    
    def handle_get(self, request, entry_title):
        
        content_md, status_code = self.entry_service.get_entry_content(entry_title)
        
        if status_code == 404:
            return render(
                request, 
                ERROR_TEMPLATE, 
                {"status_code": status_code, 
                 "message": """The page you are looking for may have been moved, deleted,
        or possibly never existed."""}) 
        
        if status_code == 505:
            return render(
                request, 
                ERROR_TEMPLATE,
                {"status_code": status_code,
                 "message": "Something went wrong when reading the entry file."}) 
       
        return render(
            request, 
            ENTRY_TEMPLATE,
            {"entry_title": entry_title, "content": content_md})
        
   
    def handle_post(self, request, entry_title):
        # If delete button is clicked, delete it 
        if "delete" in request.POST:
            self.entry_service.delete_entry(entry_title)
            return redirect("index")
        
        # If "edit" is clicked, redirect to the corresponding page
        edit_url = reverse("edit") + f"?title={entry_title}"
        return redirect(edit_url)
        
        
class ResultRequestHandler(GetRequestHandler):
    
    def handle_get(self, request):
        query = request.GET.get("q")

        if query is None:
            return render(
                request, 
                ERROR_TEMPLATE,
                {"status_code": 400, 
                 "message": "You must enter query correctly. \n Example: /result?q=QUERY."}
            )
        
        if self.entry_service.entry_exists(query):
            # Redirect to the entry page if matched exactly
            return redirect(reverse('entry', args=[query]))
        
        # List results of any entry contains query as substring 
        matched = self.entry_service.list_all_entries(query=query, filter_substr=True)
        return render(request, RESULT_TEMPLATE, {"results": matched})
            


class NewPageRequestHandler(GeneralRequestHandler):
        
    def handle_get(self, request, form):
        return render(request, 
                  NEW_PAGE_TEMPLATE, 
                  {"form": form})
        
    def handle_post(self, request, form):
        
        if not form.is_valid():
            return HttpResponse(f"Form is invalid: {form.errors}")
        
        # Extract newly created entry data
        title = form.cleaned_data["title"]
        content = form.cleaned_data["content"]
        
        if self.entry_service.entry_exists(title):
            messages.error(request, 'This entry has already existed')
            return render(request, 
                            NEW_PAGE_TEMPLATE, 
                            {"form": form})
    
                    
        # If not existed, save to Mardown file
        # And redirect to entry page
        self.entry_service.save_entry(entry=title, content=content)
        messages.success(request, 'New entry saved!')
        return redirect(reverse('entry', args=[title]))
        

class EditRequestHandler(GeneralRequestHandler):
        
    def handle_get(self, request, entry):
        content, status_code =  self.entry_service.get_entry_content(entry)
        
        if status_code == 404:
            return render(
                request, 
                ERROR_TEMPLATE,
                {"status_code": status_code,
                 "message": "You must specify the existing entry to edit. \n Example: /edit?title=ENTRY_NAME."}) 
        
        # Then check there is no problem when reading entry content
        if status_code == 505:
             return render(
                request, 
                ERROR_TEMPLATE,
                {"status_code": status_code,
                 "message": "Something went wrong when reading the entry file."})
                
        form = EntryForm({"title": entry, "content": content})
        return render(request, 
                    EDIT_TEMPLATE, 
                    {"form": form, "title": entry} )
        
      
    def handle_post(self, request, form):
        if not form.is_valid():
            return HttpResponse(f"Form is invalid: {form.errors}")
        
        # If it's valid
        # Extract the form data and save it
        # Redirect to the entry page and display the success message
        original_title = request.POST.get("original_title")
        content = form.cleaned_data["content"]
        new_title = form.cleaned_data["title"]
        
        self.entry_service.save_entry(entry=new_title, content=content, old_entry=original_title)
       
        # Redirect to the entry page 
        messages.success(request, 'Your changes have been saved.')
        return redirect(reverse('entry', args=[new_title]))


class RandomPageRequestHandler(GetRequestHandler):
    def handle_get(self, request):
        entries = self.entry_service.list_all_entries()
        random_entry = random.choice(entries)
        return redirect(reverse('entry', args=[random_entry]))