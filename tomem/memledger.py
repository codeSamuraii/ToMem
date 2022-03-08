import hashlib
from pathlib import Path
from pymemcache import serde
from pymemcache.client import base

from .utils import get_random_word


class MemLedger:
    """In-memory ledger to keep file informations."""

    LEDGER_KEY = ':memledger:'

    def __init__(self, stored_at: str = None):
        self.memcache = base.Client('localhost', serde=serde.pickle_serde)
        self.ledger_key = stored_at or self.LEDGER_KEY
        self._check_memcache_conn()
        self._initialize_ledger()

    def _check_memcache_conn(self):
        try:
            self.memcache.version()
        except OSError:
            raise Exception('Connection to memcache impossible')

    def _initialize_ledger(self):
        if self._get_ledger() is None:
            self._set_ledger({})

    def _get_ledger(self):
        return self.memcache.get(self.ledger_key)

    def _set_ledger(self, data: dict):
        return self.memcache.set(self.ledger_key, data)

    def _delete_ledger(self):
        return self.memcache.delete(self.ledger_key)

    def _update_ledger(self, data: dict):
        ledger = self._get_ledger()
        ledger.update(data)
        return self._set_ledger(ledger)

    def _get_record(self, id: str):
        return self._get_ledger()[id]

    def _delete_record(self, id: str):
        ledger = self._get_ledger()
        ledger.pop(id)
        return self._set_ledger(ledger)

    def _new_record(self, data, id: str = None):
        id = id or get_random_word()
        return {id: data}, id

    def _add_record(self, data, id: str = None):
        record, id = self._new_record(data, id)
        self._update_ledger(record)
        return record, id

    def new_file_record(self, path: Path, blob: bytes, custom_id: str = None):
        file_info = {
            'name': path.name,
            'size': len(blob),
            'checksum': hashlib.md5(blob).hexdigest()
        }
        record, id = self._add_record(file_info, custom_id)
        return id, file_info

    def get_file_record(self, id: str):
        return self._get_record(id)

    def delete_file_record(self, id: str):
        return self._delete_record(id)

    def clear_ledger(self):
        self._delete_ledger()

    def get_all_ids(self):
        return self._get_ledger().keys()

    def get_memory_usage(self):
        ledger = self._get_ledger()
        return sum(value['size'] for key, value in ledger.items())
