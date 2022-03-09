import argparse

from tomem.utils import size_format
from tomem.memstore import *


def get_command_arguments():
    parser = argparse.ArgumentParser(
        description='''Store and retrieve files in memory using memcached.
                    \rEither specify a path to a file to store it or an ID to retrieve.''',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--retrieve', metavar=('id', 'dest'), nargs='+', help='ID of the file to retrieve')
    group.add_argument('--store', metavar=('file', 'id'), nargs='+', help='file to store with optional custom ID')
    group.add_argument('--flush-all', action='store_true', help='wipes all files stored in memory')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_command_arguments()

    if args.store:
        files = set(args.store)
        path_only = {path for path in files if '::' not in path}
        with_id = dict(id_and_path.split('::') for id_and_path in files.difference(path_only))
        store = MemStore(*path_only, **with_id)
        print('\n'.join(f'* {id} - {filename}' for id, filename in store.list_files().items()))
    elif args.retrieve:
        store = MemStore()
        for file in set(args.retrieve):
            store.retrieve_file(file)
    else:
        store = MemStore()
        n, s = store.flush_all()
        print(f'{n} items deleted freeing {size_format(s)}')
