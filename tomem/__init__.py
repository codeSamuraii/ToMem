"""Store files in memory with `memcached`_.

Uses a ledger to keep track of stored files informations such as name, size and
checksum to ensure data integrity.
A custom uid can be provided (using the `uid::/file/path` format) otherwise a
human-readable one will be provided.

*This is a personal project and a work in progress.*

Examples:
::

    # Store files (specify custom uid with `::` prefix)
    $ python tomem --store images/cat.png ./report.xls customid::/tmp/data.bin

    # Retrieve files using their uids
    $ python tomem --retrieve butcheress oversteer
    $ ls -l
    cat.png report.xls

    # List stored files
    $ python tomem --list
    * butcheress - cat.png
    * oversteer - report.xls
    * customid - data.bin

    # Wipe every file from memory
    $ python tomem --flush-all
    3 items deleted freeing 1.4MiB

A Python API is available through the :class:`~tomem.api.memstore.MemStore` class.

.. _memcached: https://memcached.org/

"""
