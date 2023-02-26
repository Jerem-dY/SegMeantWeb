# -*- coding: utf-8 -*-

import shelve
from .benchmark import timeit
import os
import sys

sys.setrecursionlimit(4000)


class CacheSM:

    @timeit
    def __init__(self):
        self.cache = shelve.open("SegMeant/data/cache/cache", writeback=True)
        self.writeback = True
    pass

    def add(self, element, id: str) -> None:
        self.cache[id] = element
    pass

    def delete(self, id: str) -> None:
        if id in self.cache:
            del self.cache[id]
    pass

    def clear(self) -> None:
        self.cache.clear()
    pass

    def isin(self, id) -> bool:
        return True if id in self.cache else False
    pass

    def __del__(self):
        if not self.cache.writeback:
            self.cache.close()
    pass

    @staticmethod
    def get_corpus_id(paths: list) -> str:
        return '|'.join(sorted([os.path.basename(p) for p in paths]))
    pass
pass