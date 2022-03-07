"""
Functions to fetch random words from system dict.
"""
import random


def get_random_word():
    with open('/usr/share/dict/words', mode='r', buffering=1) as lexicon:
        lexicon_size = int(2.4e6)
        line = get_random_line(lexicon, 0, lexicon_size)
        return line.replace('\n', '').lower()


def get_random_line(fd, a, b):
    fd.seek(random.randint(a, b))
    fd.readline()
    return fd.readline()


def get_random_words(n: int):
    return [get_random_word() for i in range(n)]
