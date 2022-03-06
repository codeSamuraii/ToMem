import os
import random
from pathlib import Path
from pymemcache import serde
from pymemcache.client import base


class RandomWords:

    @staticmethod
    def random_words():
        with open('/usr/share/dict/words', mode='r', buffering=1) as words:
            random_position = random.choice(range(int(2e6)))
            words.seek(random_position)
            yield RandomWords.filter_and_clean(words.readline())

    @staticmethod
    def filter_and_clean(line: str):
        clean = line.replace('\n', '')
        if len(clean) < 4:
            return RandomWords.filter_and_clean(next(RandomWords.random_words()))
        else:
            return clean


class MemoryStore:
    """
    Easy interface to store files in memory with memcached.

    """

    def __init__(self, path: Path = None, id: str = None):
        self.memcache = base.Client('localhost', serde=serde.pickle_serde)
        self.initialize_ledger()

        self.path = path
        self.id = id

    @property
    def ledger(self):
        return self.memcache.get('ledger')

    def set_ledger(self, data: dict):
        return self.memcache.set('ledger', data)

    def update_ledger(self, data: dict):
        self.ledger.update(data)
        return self.set_ledger(data)

    def initialize_ledger(self):
        if not self.ledger:
            self.set_ledger({})

    def get_ledger_size(self):
        return len(self.ledger)

    def get_next_id(self):
        return str(self.get_ledger_size()).zfill(4)

    def new_record(self):
        self.id = self.id or self.get_next_id()
        return {self.id: self.path.name}

    def add_record_to_ledger(self):
        record = self.new_record()
        return self.update_ledger(record)

    def get_record_from_ledger(self):
        return self.ledger[self.id]

    def delete_record_from_ledger(self):
        self.ledger.pop(self.id)
        return self.update_ledger(self.ledger)

    def add_entry_to_memory(self, data):
        return self.memcache.set(self.id, data)

    def get_entry_from_memory(self):
        return self.memcache.get(self.id)

    def file_to_memory(self):
        self.add_record_to_ledger()
        blob = self.path.read_bytes()
        self.add_entry_to_memory(blob)
        return self.id

    def memory_to_file(self):
        name = self.get_record_from_ledger()
        blob = self.get_entry_from_memory()
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
