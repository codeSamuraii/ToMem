# ToMem
Store files in memory using `memcache`.

_**This is very much a work in progress !**_

## Usage
Store files :
```
$ python tomem.py --store file_1 file_2 custom_id::file_3

+ unionism - file_1
+ shovelmaker - file_2
+ custom_id - file_3
```

Retrieve files :
```
$ python tomem.py --retrieve shovelmaker custom_id
```

List stored files :
```
$ python tomem.py --list

* hippocampi - file12.jpg
* diesinking - file13.png
* special - file16.jpg
* asaphus - file12.jpg
```

Delete all files from memory:
```
$ python tomem.py --flush-all

4 items deleted freeing 11.5MiB
```
