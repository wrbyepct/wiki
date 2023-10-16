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
    content = f"""# {title}
    
{content}
"""    
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def handle_file_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FileExistsError, FileNotFoundError):
            return None
    return wrapper


@handle_file_error
def get_entry(entry, include_title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    
    If include_title is False => skip the first 2 lines of content
    """
  
    with open(f"entries/{entry}.md", "r", encoding='utf-8') as f:
        if not include_title:
            next(f)
            next(f)
        return f.read()
   
        
@handle_file_error
def delete_entry(title):
    """Directly remove the entry"""
    
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
        return {"status": "success"}
    
    return {"status": "failed", "message": f"No such file in default storage: {filename}. Old file deletion failed."}


def filter_substr(str_list, substr):
    """Given a list and a string, return any element that contains the string as substring, case insensitive
    
    """
    return [string for string in str_list if substr.lower() in string.lower()]


# def save_entry(title, content):
#     """Save the title and content as a new entry"""
#     content_md = f"""# {title}
    
# {content}
# """     
#     with open(f"entries/{title}.md", "w", encoding="utf-8") as f:
#         f.write(content_md)


