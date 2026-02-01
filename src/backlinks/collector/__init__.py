# Defining the all module for backlinks io
__all__ = ["callabledict", "book", "document"]

from backlinks.collector.book import BookDictionary
from backlinks.collector.callabledict import CallableDict
from backlinks.collector.document import FileDictionary
