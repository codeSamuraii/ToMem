import hashlib
from pymemcache import serde
from pymemcache.client import base

from utils import get_random_word


class MemLedger:
    """In-memory ledger to keep file informations."""

    DEFAULT_MEMCACHE_KEY = ':memledger:'

    def __init__(self, stored_at: str = None):
        self.memcache = base.Client('localhost', serde=serde.pickle_serde)
        self.ledger_key = stored_at or self.DEFAULT_MEMCACHE_KEY
        self._check_memcache_conn()
        self._initialize_ledger()

    def _check_memcache_conn(self):
        try:
            self.memcache.version()
        except OSError:
            raise Exception('Connection to memcache impossible.')

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

    def _get_record(self, uid: str):
        return self._get_ledger()[uid]

    def _get_file_record(self, uid: str):
        return self._get_record(uid).values()

    def _build_record(self, data, uid: str = None):
        uid = uid or get_random_word()
        return uid, {uid: data}

    def _build_file_record(self, filename: str, blob: bytes, uid: str = None):
        file_info = {'name': filename, 'size': len(blob), 'checksum': self._md5(blob)}
        return self._build_record(file_info, uid)

    def _add_record(self, data, uid: str = None):
        uid, record = self._build_record(data, uid)
        self._update_ledger(record)
        return uid, record

    def _add_file_record(self, filename: str, blob: bytes, uid: str = None):
        uid, record = self._build_file_record(filename, blob, uid)
        self._update_ledger(record)
        return uid, record

    def _md5(self, blob):
        return hashlib.md5(blob).hexdigest()

    def get_memory_usage(self):
        ledger = self._get_ledger()
        return sum(value['size'] for key, value in ledger.items())
