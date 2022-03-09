import os
from pathlib import Path

from .memledger import MemLedger


class MemStore(MemLedger):

    def __init__(self, *args, stored_at: str = None, **kwargs):
        MemLedger.__init__(self, stored_at)

        for path in args:
            self.add_file(path)
        for id, path in kwargs.items():
            self.add_file(path, id)

    def _store_file_data(self, id: str, data: bytes):
        return self.memcache.set(id, data)

    def _retrieve_file_data(self, id: str, checksum: str):
        blob = self.memcache.get(id)
        if self._md5(blob) == checksum:
            return blob
        else:
            raise Exception()

    def _get_readable_path(self, path: str = ''):
        path = Path(path)
        if path.is_file() and os.access(path, os.R_OK):
            return path
        else:
            raise Exception(f'Unable to read file: {path}')

    def _get_writable_path(self, path: Path, name: str):
        if path is None and name != '':
            return Path.cwd() / name
        if path.is_dir():
            return path / name
        if path.parent.is_dir() and not path.is_file():
            path.touch()
            return path
        else:
            raise Exception()

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
        return {key: value['name'] for key, value in self._get_ledger()}
