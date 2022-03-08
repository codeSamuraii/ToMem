import argparse
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
    return parser.parse_args()


if __name__ == '__main__':
    args = get_command_arguments()

    if args.store:
        store_in_memory(*args.store)
    else:
        retrieve_file(*args.retrieve)
