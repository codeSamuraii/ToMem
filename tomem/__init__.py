"""Store files in memory with `memcached`_.

Uses a ledger to keep track of stored files informations such as name, size and checksum
to ensure data integrity. A custom uid can be provided when storing a file, otherwise a human-readable
one will be provided.

Examples:

    $ python tomem --store images/file10.png
    * butcheress - file10.png

A Python API is available through the :py:class:`tomem.api.MemStore` class.

.. _memcached: https://memcached.org/

"""
