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


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def filter_substr(str_list, substr):
    return [string for string in str_list if substr.lower() in string.lower()]


def save_new_entry(title, content):
    content_md = f"""# {title}
    
{content}
"""     
    with open(f"entries/{title}.md", "w", encoding="utf-8") as f:
        f.write(content_md)

def delete_entry(entry):
    os.remove(f"entries/{entry}.md")