
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from http import HTTPStatus

import random
from abc import ABC, abstractmethod

from .constant import *
from .form import EntryForm
from .service import EntryService

class ResponseRenderer:
    
    def render_page(self, request, template, data: dict):
        return render(request, template, data)
    
    def render_error(self, request, status_code, message):
        return render(request, ERROR_TEMPLATE,  
                        {"status_code": status_code, 
                         "message": message})
    
    
class GetRequestHandler(ABC):
    def __init__(self, entry_service: EntryService=None, renderer: ResponseRenderer=None):
        self.entry_service = entry_service or EntryService()
        self.renderer = renderer or ResponseRenderer()
        
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
        
        if status_code == HTTPStatus.NOT_FOUND:
            return self.renderer.render_error(
                request=request,
                status_code=HTTPStatus.NOT_FOUND,
                message="""The page you are looking for may have been moved, deleted, \
or possibly never existed.""")
           
           
        if status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            return self.renderer.render_error(request=request,
                                     status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                     message="Something went wrong when reading the entry file.")

            
        return self.renderer.render_page(
            request, 
            ENTRY_TEMPLATE,
            {"content": content_md})
        
   
    def handle_post(self, request, entry_title):
        
        # Ensure user can delete the orginal title name 
        # even though they don't request entry adhering to the entry case
        # e.g. They type 'pyThoN', they can still get 'Pyhton' 
        original_entry_name = self.entry_service.get_original_entry_name(entry_title)
        
        # In case the user somehow gets to post none existing entry
        if original_entry_name is None:
            self.renderer.render_error(request=request,
                              status_code=404,
                              message="""The page you are looking for may have been moved, deleted,
        or possibly never existed.""")
        
        # If delete button is clicked, delete it 
        if "delete" in request.POST:
            self.entry_service.delete_entry(original_entry_name)
            messages.success(request, "The entry was successfully deleted.")
            return redirect("index")
        
        # If "edit" is clicked, redirect to the corresponding page
        return redirect(reverse("edit", args=[original_entry_name]))
        
        
class ResultRequestHandler(GetRequestHandler):
    
    def handle_get(self, request):
        query = request.GET.get("q")

        # If the user access /result without query 
        if query is None:
            return self.renderer.render_error(
                request=request, 
                status_code=HTTPStatus.BAD_REQUEST, 
                message="You must enter query correctly. \n Example: /result?q=QUERY."
            )
           
        if self.entry_service.entry_exists(query):
            # Redirect to the entry page if matched exactly
            return redirect(reverse('entry', args=[query]))
        
        # List results of any entry contains query as substring 
        matched = self.entry_service.list_all_entries(query=query, filter_substr=True)
        return self.renderer.render_page(request, RESULT_TEMPLATE, {"results": matched})
            

class NewPageRequestHandler(GeneralRequestHandler):
    
    def handle_get(self, request, form):
        return self.renderer.render_page(
            request, 
            NEW_PAGE_TEMPLATE, 
            {"form": form})
        
    def handle_post(self, request, form):
        
        # If the field does not adhere specification, warn user
        # e.g.: Exceeding character count
        if not form.is_valid():
            messages.error(request, f"{form.errors.as_text()}")
            return self.renderer.render_page(
                request, 
                NEW_PAGE_TEMPLATE, 
                 {"form": form}
            )
        
        # Extract newly created entry data
        title = form.cleaned_data["title"]
        content = form.cleaned_data["content"]
        
        if self.entry_service.entry_exists(title):
            
            messages.error(request, 'WARNING: This entry has already existed!')
            return self.renderer.render_page(
                request, 
                NEW_PAGE_TEMPLATE, 
                {"form": form}
            )
    
                    
        # If not existed, save to Mardown file
        # And redirect to entry page
        _ = self.entry_service.save_entry(entry=title, content=content)
        
        # And save the save the entries that's also created in content 
        self.entry_service.save_all_new_entries(content=content)
        
        messages.success(request, 'New entry saved!')
        return redirect(reverse('entry', args=[title]))
        

class EditRequestHandler(GeneralRequestHandler):
        
    def handle_get(self, request, entry):
        content, status_code =  self.entry_service.get_entry_content(entry=entry, include_title=False)
        
        if status_code == 404:
            return self.renderer.render_error(
                request, 
                status_code=HTTPStatus.NOT_FOUND,
                message= "You must specify an existing entry to edit. \n Example: /edit/ENTRY_NAME."
            ) 
        
        # Then check there is no problem when reading entry content
        if status_code == 505:
            return self.renderer.render_error(
                request, 
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Something went wrong when reading the entry file."
            ) 
                
        form = EntryForm({"title": entry, "content": content})
        return self.renderer.render_page(
            request, 
            EDIT_TEMPLATE, 
            {"form": form, "title": entry}
        )
        
      
    def handle_post(self, request, form):
        if not form.is_valid():
            return HttpResponse(f"Form is invalid: {form.errors}")
        
        # If it's valid
        # Extract the form data and save it
        # Redirect to the entry page and display the success message
        original_title = request.POST.get("original_title")
        content = form.cleaned_data["content"]
        new_title = form.cleaned_data["title"]
        
        result = self.entry_service.save_entry(entry=new_title, content=content, old_entry=original_title)

        # Handle if there is an error when saving file
        if result["status"] != "success":
            
            return self.renderer.render_error(
                request=request,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message= f"{result['message']} Saving process aborted."
            )
            
        # And save the save the entries that's also created in content
        self.entry_service.save_all_new_entries(content=content)     
       
        # Redirect to the entry page 
        messages.success(request, 'Your changes have been saved.')
        return redirect(reverse('entry', args=[new_title]))


class RandomPageRequestHandler(GetRequestHandler):
    def handle_get(self, request):
        entries = self.entry_service.list_all_entries()
        
        if not entries:
            return self.renderer.render_error(
                request=request,
                status_code=HTTPStatus.BAD_GATEWAY,
                message="There is no entry yet! Let's create some page."
            )
        
        random_entry = random.choice(entries)
        return redirect(reverse('entry', args=[random_entry]))