import argparse
from filestore import *


def get_command_arguments():
    parser = argparse.ArgumentParser(
        description='''Store and retrieve files in memory using memcached.
                    \rEither specify a path to a file to store it or an ID to retrieve.''',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--retrieve', metavar='id', help='ID of the file to retrieve')
    group.add_argument('--store', metavar=('file', 'id'), nargs='+', help='file to store with optional custom ID')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_command_arguments()
    store_args = args.store
    retrieve_args = args.retrieve

    if store_args:
        file = store_args.pop(0)
        custom_id = store_args.pop() if store_args else None
        storage_id = store_in_memory(file, custom_id)
        print(f'File stored with ID: {storage_id}')
    else:
        storage_id = retrieve_args
        file_name = retrieve_file(storage_id)
        print(f'File with ID {storage_id} retrieved: {file_name}')
