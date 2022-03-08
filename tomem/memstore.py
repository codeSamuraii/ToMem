import os
import random
import hashlib

from pathlib import Path
from pymemcache import serde
from pymemcache.client import base

from .utils import size_format
from .memledger import MemLedger


class MemStore:
    """Easy interface to store files in memory with memcached."""

    def __init__(self, path: str = None, id: str = None, ledger: str = None):
        self.memcache = base.Client('localhost', serde=serde.pickle_serde)
        self.ledger = MemLedger(stored_at=ledger)
        self.path = Path(path) if path else None
        self.id = id

    def _store_in_memory(self, data):
        return self.memcache.add(self.id, data)

    def _retrieve_from_memory(self, id):
        return self.memcache.get(id)

    def _delete_from_memory(self, id):
        return self.memcache.delete(id)

    def clear(self):
        file_ids = self.ledger.get_all_ids()
        for id in file_ids:
            self._delete_from_memory(id)
        self.ledger.clear_ledger()
        return file_ids

    @classmethod
    def memory_usage(cls):
        size_bytes = cls.LEDGER.get_memory_usage()
        readable_size = size_format(size_bytes)
        print(readable_size)
        return size_bytes

    def _verify_checksum(self, control: str, file: bytes):
        checksum = hashlib.md5(file).hexdigest()
        return checksum == control

    def _create_file(self, name: str, blob: bytes):
        dest = self.path or Path.cwd() / name
        dest.touch(exist_ok=False)
        dest.write_bytes(blob)

    def _file_to_memory(self):
        blob = self.path.read_bytes()
        self.id, file_info = self.ledger.new_file_record(self.path, blob, self.id)
        self._store_in_memory(blob)
        return self.id, file_info

    def _memory_to_file(self):
        blob = self._retrieve_from_memory(self.id)
        record = self.ledger.get_file_record(self.id)
        name, size, checksum = record.values()
        self._create_file(name, blob)

        if not self._verify_checksum(checksum, blob):
            raise Exception('Checksums mismatch - file or record corrupted')

        return record

    @classmethod
    def read_file(cls, file_path: str, id: str = None):
        store = cls(path=file_path, id=id)
        id, record = store._file_to_memory()
        return id, record

    @classmethod
    def from_id(cls, id: str, dest: str = None) :
        store = cls(path=dest, id=str(id))
        record = store._memory_to_file()
        store.ledger.delete_file_record(id)
        return record



def store_in_memory(file_path: str, id: str = None, delete=False):
    id, file_info = MemStore.read_file(file_path, id)
    display = ' - '.join(f'{key}: {value}' for key, value in file_info.items())
    print(f"[+] id: {id} | {display}")

    if delete:
        os.remove(file_path)

    return id


def retrieve_file(id: str, dest: str = None):
    file_info = MemStore.from_id(id, dest)
    display = ' - '.join(f'{key}: {value}' for key, value in file_info.items())
    print(f"[-] id: {id} | {display}")
    return file_info
