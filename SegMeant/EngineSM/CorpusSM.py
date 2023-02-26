# -*- coding: utf-8 -*-

from .SegmentedTextSM import SegmentedTextSM
from .statistics.StatisticsSM import dist_matrix, distance_methods
import os
import numpy as np

class CorpusSM:


    def __init__(self, documents: list):

        self.documents: list = []
        self.matrices: dict = {}

        for i, doc in enumerate(documents):

            if isinstance(doc, SegmentedTextSM):
                self.documents.append(doc)
                continue

            if os.path.isfile(doc):
                with open(doc, mode='r', encoding='utf-8') as f:
                    print(f"\n\n##### Texte {i} : \"{doc}\"")
                    self.documents.append(SegmentedTextSM(f, doc_name=doc))

        self.matrices = dist_matrix([i.types.stats.ngrams['1'] for i in self.documents])
    pass


pass