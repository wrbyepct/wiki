
from .dao import EntryDao
from . import util


class EntryService:
    def __init__(self, dao=None):
        self.dao = dao or EntryDao
    
    
    def list_all_entries(self, query="", filter_substr=False):
        entries = self.dao.fetch_all_entries()
        
        if filter_substr:
            matched = util.filter_substr(str_list=entries, substr=query)
            return matched
        
        return entries
    
    
    def get_entry_content(self, entry, include_title=True):
        
        entries = [entry.lower() for entry in self.list_all_entries()]
        
        if entry.lower() not in entries:
            return None, 404
        
        content = self.dao.fetch_entry(entry, include_title)
        
        if content is None:
            return None, 505
        
        return content, 200
    
   
    def save_entry(self, entry, content, old_entry=None):
        
        if old_entry and (entry != old_entry):
            self.dao.delete_entry(old_entry)
                
        self.dao.save_entry(entry, content)
    
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