
from http import HTTPStatus
from .dao import DataDao, EntryDao
from . import util


class EntryService:
    def __init__(self, dao: DataDao=None):
        self.dao = dao or EntryDao
        
    
    def list_all_entries(self, query="", filter_substr=False):
        entries = self.dao.fetch_all_entries()
        
        if filter_substr:
            matched = util.filter_substr(str_list=entries, substr=query)
            return matched
        
        return entries
    
    
    def get_entry_content(self, entry, include_title=True):
        
        entries = [entry.lower() for entry in self.list_all_entries()]
        
        # If no such entry, return not found
        if entry.lower() not in entries:
            return None, HTTPStatus.NOT_FOUND
        
        content = self.dao.fetch_entry(entry, include_title)
        
        # If there is problem reading files
        if content is None:
            return None, HTTPStatus.INTERNAL_SERVER_ERROR
        
        return content, HTTPStatus.OK
    
   
    def save_entry(self, entry, content, old_entry=None):
        
        if old_entry:
            result = self.dao.delete_entry(old_entry)
            if result["status"] != "success":
                return result
                
        self.dao.save_entry(entry, content)
        return {"status": "success"}
    
    
    def save_new_entries_in_content(self, content):
        
        # Find link title in content if there is any
        link_titles = util.scan_for_link_titles(content)
        
        if link_titles:
            print(f"Link titles detected: {link_titles}")
            existing_entries = self.list_all_entries()
            
            # filter out existing entries
            new_entries = util.filter_out_existing_entries(link_entries=link_titles, existings_entries=existing_entries)
            if new_entries:
                print(f"New titles detected: {new_entries}")
                self.dao.save_all_entries(new_entries)
    
    
    def delete_entry(self, entry):
        self.dao.delete_entry(entry)
        
        
    def entry_exists(self, entry):
        entries = self.list_all_entries()
        entries_lower = [entry.lower() for entry in entries]
        return entry.lower() in entries_lower
    
    
    def get_original_entry_name(self, comparing_entry):
        """Return original entry name if the given entry matches it case-insensitively
        If no such match, return None
        """
        entries = self.list_all_entries()
        for entry in entries:
            if comparing_entry.lower() == entry.lower():
                return entry
        return None