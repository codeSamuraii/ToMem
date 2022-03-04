import os
from pathlib import Path
from pymemcache import serde
from pymemcache.client import base


class MemoryStore:
    """
    Easy interface to store files in memory with memcached.

    """

    def __init__(self, path: Path = None, id: str = None):
        self.memcache = base.Client('localhost', serde=serde.pickle_serde)
        self.initialize_ledger()

        self.path = path
        self.id = id

    def initialize_ledger(self):
        if not self.memcache.get('ledger'):
            self.memcache.set('ledger', {})

    def get_ledger_size(self):
        ledger = self.memcache.get('ledger')
        return len(ledger)

    def get_next_id(self):
        return str(self.get_ledger_size()).zfill(4)

    def new_record(self):
        self.id = self.id or self.get_next_id()
        return {self.id: self.path.name}

    def add_record_to_ledger(self):
        record = self.new_record()
        ledger = self.memcache.get('ledger')
        ledger.update(record)
        self.memcache.set('ledger', ledger)
        return ledger

    def get_record_from_ledger(self):
        ledger = self.memcache.get('ledger')
        return ledger[self.id]

    def delete_record_from_ledger(self):
        ledger = self.memcache.get('ledger')
        ledger.pop(self.id)
        self.memcache.set('ledger', ledger)

    def file_to_memory(self):
        self.add_record_to_ledger()
        blob = self.path.read_bytes()
        self.memcache.set(self.id, blob)
        return self.id

    def memory_to_file(self):
        name = self.get_record_from_ledger()
        blob = self.memcache.get(self.id)
        dest = Path.cwd() / name
        dest.touch()
        dest.write_bytes(blob)
        self.delete_record_from_ledger()
        return name

    @classmethod
    def read_file(cls, file_path: str, id: str = None):
        path = Path(file_path)

        if not path.exists() or not path.is_file():
            raise ValueError('File not found.')

        holder = cls(path=path, id=id)
        holder.file_to_memory()
        return holder

    @classmethod
    def from_id(cls, id: str) :
        holder = cls(id=str(id))
        holder.memory_to_file()
        return holder



def store_in_memory(file_path: str, id: str = None, delete=False):
    holder = MemoryStore.read_file(file_path, id)
    if delete:
        os.remove(file_path)
    return holder.id


def retrieve_file(id: str):
    holder = MemoryStore.from_id(id)
    file_name = holder.memory_to_file()
    return file_name
