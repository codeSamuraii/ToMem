CLI
---

ToMem can be used as a command to store and retrieve files in memory.

Examples
+++++++++

.. code-block:: bash
   :emphasize-lines: 3,4,5,10,14,15,16,20

   # Store files (specify custom uid with `::` prefix)
   $ python tomem --store images/cat.png ./report.xls customid::/tmp/data.bin
   * butcheress - cat.png
   * oversteer - report.xls
   * customid - data.bin

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
