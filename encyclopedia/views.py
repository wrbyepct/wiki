from django.contrib import messages
from django.shortcuts import render, redirect
from . import util


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
            to_edit = request.POST.get("edit")
            
            print(f"To edit is pressed: {to_edit}")
            return redirect("index")

    else:
        entries = [entry.lower() for entry in util.list_entries()]
        
        # Handle entry exists or not
        if entry_title.lower() in entries:
            content_md = util.get_entry(title=entry_title)
            return render(request, "encyclopedia/entry.html",
                    {"entry_title": entry_title, "content": content_md})
        else:
            return render(request, "encyclopedia/page_not_found.html")
    
def render_results(request):
    # if request.method == 'POST':
    query = request.POST.get("q")
    entries = util.list_entries()
    entries_lower = [entry.lower() for entry in entries]
    
    # Redirect to the entry page if matched 
    if query.lower() in entries_lower:
        print("Search matched")
        return redirect(f"/wiki/{query}")
    
    # List results if the query match the entry substring 
    matched = util.filter_substr(str_list=entries, substr=query)
    
    return render(request, "encyclopedia/result.html", {"results": matched})

def render_new_page(request):
    if request.method == "POST":
        # Extract newly created entry data
        data = request.POST
        title = data.get("title")
        content = data.get("content")
        
        # Save to Mardown file
        util.save_new_entry(title=title, content=content)
        messages.success(request, 'Your changes were saved.')
        return redirect("/newpage")
    return render(request, "encyclopedia/new_page.html")