import os
from pathlib import Path

from .memledger import MemLedger


class MemStore(MemLedger):

    def __init__(self, *args, stored_at: str = None, **kwargs):
        super().__init__(stored_at)
        self.history = {}

        for path in args:
            id, record = self.store_file(path)
            self.history[id] = record[id]['name']
        for id, path in kwargs.items():
            id, record = self.store_file(path, id)
            self.history[id] = record[id]['name']

    def _store_file_data(self, id: str, data: bytes):
        return self.memcache.set(id, data)

    def _retrieve_file_data(self, id: str, checksum: str):
        blob = self.memcache.get(id)
        if self._md5(blob) != checksum:
            raise Exception("Checksums don't match. File may be corrupted.")
        return blob

    def _delete_file_data(self, id: str):
        return self.memcache.delete(id)

    def _get_readable_path(self, path: str = ''):
        path = Path(path)
        if not path.is_file() or not os.access(path, os.R_OK):
            raise Exception(f'Unable to read file: {path}')
        return path


    def _get_writable_path(self, path: Path, name: str):
        if path is None and name != '':
            return Path.cwd() / name
        elif path.is_dir():
            return path / name
        elif path.parent.is_dir() and not path.is_file():
            path.touch()
            return path
        raise Exception('Invalid path or filename already in use.')

    def _read_file(self, path: str):
        source = self._get_readable_path(path)
        return source.name, source.read_bytes()

    def _write_file(self, blob: bytes, path: Path = None, name: str = ''):
        dest = self._get_writable_path(path, name)
        return dest.write_bytes(blob)

    def store_file(self, path: str, id: str = None):
        filename, blob = self._read_file(path)
        id, record = self._add_file_record(filename, blob, id)
        self._store_file_data(id, blob)
        return id, record

    def retrieve_file(self, id: str, path: str = None):
        name, size, checksum = self._get_file_record(id)
        blob = self._retrieve_file_data(id, checksum)
        written = self._write_file(blob, path, name)
        assert written == size

    def list_files(self):
        return {id: record['name'] for id, record in self._get_ledger().items()}

    def flush_all(self):
        cleared = self.get_memory_usage()
        ids = self._get_ledger().keys()
        for id in ids:
            self._delete_file_data(id)
        self._delete_ledger()
        return len(ids), cleared
