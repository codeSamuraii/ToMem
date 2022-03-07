from pymemcache import serde
from pymemcache.client import base

from.randomwords import get_random_word


class MemoryLedger:
    """In-memory ledger to keep file informations."""

    MEMCACHE_KEY = ':ledger:'

    def __init__(self):
        self.memcache = base.Client('localhost', serde=serde.pickle_serde)
        self.initialize_ledger()

    def initialize_ledger(self):
        if self.get_ledger() is None:
            self.set_ledger({})

    def get_ledger(self):
        return self.memcache.get(self.MEMCACHE_KEY)

    def set_ledger(self, data: dict):
        return self.memcache.set(self.MEMCACHE_KEY, data)

    def update_ledger(self, data: dict):
        ledger = self.get_ledger()
        ledger.update(data)
        return self.set_ledger(ledger)

    def get_ledger_size(self):
        return len(self.get_ledger())

    def get_record(self, id: str):
        return self.get_ledger()[id]

    def delete_record(self, id: str):
        ledger = self.get_ledger()
        ledger.pop(id)
        return self.set_ledger(ledger)

    def new_record(self, data, id: str = None):
        id = id or get_random_word()
        return {id: self.path.name}

    def add_record(self, data, id: str = None):
        record = self.new_record(data, id)
        self.update_ledger(record)
        return record
