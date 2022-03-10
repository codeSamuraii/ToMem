import os
from pathlib import Path

from .memledger import MemLedger


class MemStore(MemLedger):
    """Python API to store files in memory using `memcached`.

    Uses a file ledger to keep track of stored file informations such as _name_, _size_ and _MD5 checksum_
    to ensure data integrity. A custom id can be provided when storing a file, otherwise a human-readable
    one will be provided.

    Args:
        ledger_key (:obj:`str`, optional): Connect to an existing ledger or create one with specified key.
        *args: Paths of files to store. A random id will be used for each.
        **kwargs: Paths of files to be stored with a specific id.

    """

    def __init__(self, ledger_key: str = None, *args, **kwargs):
        super().__init__(ledger_key)

        for path in args:
            id, record = self.store_file(path)
        for id, path in kwargs.items():
            id, record = self.store_file(path, id)

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
        """Store a file in memory.

        Args:
            path (str): Path to the file.
            id (:obj:`str`, optional): Specify a custom id for the file.

        Returns:
            :rtype: (str, dict): id of the file and record added to the ledger.

        """
        filename, blob = self._read_file(path)
        id, record = self._add_file_record(filename, blob, id)
        self._store_file_data(id, blob)
        return id, record

    def retrieve_file(self, id: str, path: str = None):
        """Retrieve a file from memory.

        Args:
            id (str): ID of the file.
            path (:obj:`str`, optional): Custom path for file creation.

        Note:
            `path` must point to a directory or a non-existent file.

        """
        name, size, checksum = self._get_file_record(id)
        blob = self._retrieve_file_data(id, checksum)
        written = self._write_file(blob, path, name)

    def stored_files(self):
        """Fetch a mapping of stored files.

        Returns:
            dict: id and filename for every stored file.

        """
        return {id: record['name'] for id, record in self._get_ledger().items()}

    def flush_all(self):
        """Delete every file stored in memory.

        Returns:
            :obj:`tuple` of :obj:`int`: Number of files removed and total bytes freed from memory.

        """
        cleared = self.get_memory_usage()
        ids = self._get_ledger().keys()
        for id in ids:
            self._delete_file_data(id)
        self._delete_ledger()
        return len(ids), cleared
