import sys
import argparse

from api.utils import size_format, display_dict
from api import MemStore


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
    group.add_argument('--list', action='store_true', help='lists all files stored')
    return parser.parse_args()


def store(files):
    path_only = {path for path in files if '::' not in path}
    with_id = dict(id_and_path.split('::') for id_and_path in files.difference(path_only))
    store = MemStore.from_files(*path_only, **with_id)


def retrieve(uids):
    store = MemStore()
    for uid in uids:
        store.retrieve_file(uid)


def list_entries():
    store = MemStore()
    display_dict(store.stored_files())


def flush():
    store = MemStore()
    n, s = store.flush_all()
    print(f'{n} items deleted freeing {size_format(s)}')


def main():
    args = get_command_arguments()

    if args.store:
        store(set(args.store))
    elif args.retrieve:
        retrieve(set(args.retrieve))
    elif args.list:
        list_entries()
    else:
        flush()


if __name__ == '__main__':
    sys.exit(main())
