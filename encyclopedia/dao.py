from abc import ABC, abstractmethod
from . import util

class DataDao(ABC):
    @abstractmethod
    def fetch_all_entries():
        pass
    
    @abstractmethod
    def fetch_entry(entry):
        pass
    
    @abstractmethod
    def save_entry(entry, content):
        pass
    
    @abstractmethod
    def delete_entry(entry):
        pass


class EntryDao(DataDao):
    
    @staticmethod
    def fetch_all_entries():
        return util.list_entries()
    
    @staticmethod
    def fetch_entry(entry, include_title: bool):
        return util.get_entry(entry, include_title)
    
    @staticmethod
    def save_entry(entry, content):
        return util.save_entry(entry, content)
    
    @staticmethod
    def delete_entry(entry):
        util.delete_entry(entry)
        
        

