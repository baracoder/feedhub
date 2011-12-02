__all__ = ['default', ]

class Item(object): 
    def __repr__(self): return getattr(self, 'title', 'Untitled').encode('utf-8', 'replace')
    __str__ = __repr__

