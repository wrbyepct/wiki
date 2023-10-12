import re
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    a = default_storage.listdir("entries")
    # The first it gives you the subdirs names
    _, filenames = default_storage.listdir("entries")
    
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def handle_file_error(func):
    def wrapper(title, include_title=True):
        try:
            with open(f"entries/{title}.md", "r", encoding='utf-8') as f:
                return func(f, include_title)
        except (FileExistsError, FileNotFoundError):
            return None
    return wrapper


@handle_file_error
def get_entry(f, include_title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    
    If include_title is False => skip the first 2 lines of content
    """
    if not include_title:
        next(f)
        next(f)
    return f.read()
    

def filter_substr(str_list, substr):
    """Given a list and a string, return any element that contains the string as substring, case insensitive
    
    """
    return [string for string in str_list if substr.lower() in string.lower()]


def save_entry(title, content):
    """Save the title and content as a new entry"""
    content_md = f"""# {title}
    
{content}
"""     
    with open(f"entries/{title}.md", "w", encoding="utf-8") as f:
        f.write(content_md)


def save_edit(original_title, new_title, content):
    """Handle edit entry 
    
    1. If it's with new title, delete the old one and create the new one.
    2. If the titles are the same, then directly overwrite it.
    """
    
    # If the title has changed
    # Delete the old one and create the new one
    if new_title != original_title:
        delete_entry(original_title)
        
    # Afte that, create the new one or overwrite the content
    save_entry(title=new_title, content=content)

def delete_entry(entry):
    """Directly remove the entry"""
    os.remove(f"entries/{entry}.md")