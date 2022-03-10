import os
from pathlib import Path
from typing import Tuple

from .memledger import MemLedger


class MemStore(MemLedger):
    """Python API to store files in memory using `memcached`.

    Uses a file ledger to keep track of stored file informations such as _name_, _size_ and _MD5 checksum_
    to ensure data integrity. A custom uid can be provided when storing a file, otherwise a human-readable
    one will be provided.

    Args:
        ledger_key (:obj:`str`, optional): Connect to an existing ledger or create one with specified key.
        *args: Paths of files to store. A random uid will be used for each.
        **kwargs: Paths of files to be stored with a specific uid.

    """

    def __init__(self, ledger_key: str = None, *args: str, **kwargs: str):
        super().__init__(ledger_key)

        for path in args:
            uid, record = self.store_file(path)
        for uid, path in kwargs.items():
            uid, record = self.store_file(path, uid)

    def _store_file_data(self, uid: str, data: bytes) -> bool:
        return self.memcache.set(uid, data)

    def _retrieve_file_data(self, uid: str, checksum: str) -> bytes:
        blob = self.memcache.get(uid)
        if self._md5(blob) != checksum:
            raise Exception("Checksums don't match. File may be corrupted.")
        return blob

    def _delete_file_data(self, uid: str) -> bool:
        return self.memcache.delete(uid)

    def _get_readable_path(self, location: str = '') -> Path:
        path = Path(location)
        if not path.is_file() or not os.access(path, os.R_OK):
            raise Exception(f'Unable to read file: {path}')
        return path

    def _get_writable_path(self, location: str = '', name: str = '') -> Path:
        path = Path(location)

        if path is None and name != '':
            return Path.cwd() / name

        if path.is_dir():
            return path / name

        if path.parent.is_dir() and not path.is_file():
            path.touch()
            return path

        raise Exception('Invalid path or filename already in use.')

    def _read_file(self, path: str) -> Tuple[str, bytes]:
        source = self._get_readable_path(path)
        return source.name, source.read_bytes()

    def _write_file(self, blob: bytes, path: str = '', name: str = '') -> int:
        dest = self._get_writable_path(path, name)
        return dest.write_bytes(blob)

    def store_file(self, path: str, uid: str = '') -> Tuple[str, dict]:
        """Store a file in memory.

        Args:
            path (str): Path to the file.
            uid (:obj:`str`, optional): Specify a custom uid for the file.

        Returns:
            :rtype: (str, dict): uid of the file and record added to the ledger.

        """
        filename, blob = self._read_file(path)
        uid, record = self._add_file_record(filename, blob, uid)
        self._store_file_data(uid, blob)
        return uid, record[uid]

    def retrieve_file(self, uid: str, path: str = ''):
        """Retrieve a file from memory.

        Args:
            uid (str): uid of the file.
            path (:obj:`str`, optional): Custom path for file creation.

        Note:
            `path` must point to a directory or a non-existent file.

        """
        name, size, checksum = self._get_file_record(uid)
        blob = self._retrieve_file_data(uid, checksum)
        written = self._write_file(blob, path, name)
        if written != size:
            raise Exception("Sizes don't match. File may be corrupted.")

    def stored_files(self) -> dict:
        """Fetch a mapping of stored files.

        Returns:
            dict: uid and filename for every stored file.

        """
        return {uid: record['name'] for uid, record in self._get_ledger().items()}

    def flush_all(self) -> Tuple[int, int]:
        """Delete every file stored in memory.

        Returns:
            :obj:`tuple` of :obj:`int`: Number of files removed and total bytes freed from memory.

        """
        cleared = self.get_memory_usage()
        ids = self._get_ledger().keys()
        for uid in ids:
            self._delete_file_data(uid)
        self._delete_ledger()
        return len(ids), cleared
