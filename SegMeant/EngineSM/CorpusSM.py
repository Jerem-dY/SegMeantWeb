# -*- coding: utf-8 -*-

from .SegmentedTextSM import SegmentedTextSM
from .classification import ClassificationSM
import os

class CorpusSM:
    """
    Classe représentant un ensemble de textes tokenisés et étiquetés, et permettant des traitements groupés ainsi que des tâches de classification.

    :param documents: une liste de documents bruts ou traités que l'on souhaite rassembler
    :type documents: une liste de str ou de :class:`SegmentedTextSM` (pouvant être mélangés)
    """


    def __init__(self, documents: list):
        """
        Constructeur de la classe.
        """

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

        self.matrices = ClassificationSM.dist_matrix([i.types.stats.ngrams['1'] for i in self.documents])
    pass


pass