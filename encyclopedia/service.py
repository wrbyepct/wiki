
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
    
    def entry_exists(self, entry):
        entries = self.list_all_entries()
        entries_lower = [entry.lower() for entry in entries]
        return entry.lower() in entries_lower
    
    
    def get_entry_content(self, entry):
        entries = [entry.lower() for entry in self.list_all_entries()]
        
        if entry.lower() not in entries:
            return None, 404
        
        content = self.dao.fetch_entry(entry)
        
        if content is None:
            return None, 505
        
        return content, 200
    
   
    def save_entry(self, entry, content, old_entry=None):
        
        if old_entry and (entry != old_entry):
            self.dao.delete_entry(old_entry)
                
        self.dao.save_entry(entry, content)
    
    def delete_entry(self, entry):
        self.dao.delete_entry(entry)