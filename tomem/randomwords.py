"""
Functions to fetch random words from system dict.
"""
import random


def get_random_word():
    with open('/usr/share/dict/words', mode='r', buffering=1) as words:
        random_position = random.randint(0, int(2e6))
        words.seek(random_position)
        return filter_and_clean(words.readline())


def filter_and_clean(line: str):
    clean = line.replace('\n', '')
    if len(clean) < 4:
        return filter_and_clean(get_random_word())
    else:
        return clean


def get_random_words(n: int):
    return [get_random_word() for i in range(n)]
