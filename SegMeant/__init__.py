# -*- coding: utf-8 -*-
'''
INFORMATIONS GENERALES
=========================================================================
Cours de Python - M1 Sciences du Langage parcours Industries de la Langue
Projet de fin de semestre

INFORMATIONS SUR LE MODULE
=========================================================================
:auteur: Jérémy Bourdillat <Jeremy.Bourdillat@etu.univ-grenoble-alpes.fr> et Inès Adjoudj <Ines.Adjoudj@etu.univ-grenoble-alpes.fr>
:version: 1.0
Python ver. 3.11.1

OBSERVATIONS
=========================================================================
'''


from .EngineSM import SegmentedTextSM
from .EngineSM.SegmentedTextSM import SegmentedTextSM
from .EngineSM.statistics import StatisticsSM
from .EngineSM.resources.NGramsSM import NGramsSM
from .EngineSM.resources.LexiconSM import LexiconSM
from .EngineSM.CorpusSM import CorpusSM
from .EngineSM.tools.CacheSM import CacheSM
import os
import shelve
import re

catGet = re.compile(r"""
    (?:\#.*\n)*
    (
    \d{1,3}
    (?:\t\w+){2}
    \t
    (?P<cat>\w+)+
    .*\n
    )
""", flags=re.X | re.UNICODE)


class SegMeant:

    def __init__(self):
        with open("SegMeant/EngineSM/resources/fr_ftb-ud-train.conllu", mode="r", encoding="utf-8") as f:
            pg = ""
            ph = []
            for line in f:
                pg += line
                #if line == "\n":
                ph += [el[1] for el in catGet.findall(pg) if el[1]]
                pg = ""


        #self.CACHE = CacheSM()
        self.LEXICON = LexiconSM.load()
        self.MODEL = NGramsSM(dic=shelve.open("SegMeant/data/tagsStats/ngrams", writeback=False), n={2, 3, 4}, sep='+', txt=ph)
    pass

    def segment_text_from_file(self, path: str) -> SegmentedTextSM:

        with open(path, mode="r", encoding="utf-8") as f:

            txt = f.read()

            if self.CACHE.isin(txt):
                print(f"File \"{os.path.basename(path)}\" already in cache. Loading...")
                return self.CACHE.cache[txt]

            doc = SegmentedTextSM(txt, doc_name=os.path.basename(path), lexicon=self.LEXICON, model=self.MODEL)
            self.CACHE.add(doc, txt)
            return doc

    pass


    def corpus_from_paths(self, paths: list) -> CorpusSM:

        docs: list = []

        id = self.CACHE.get_corpus_id(paths)

        if self.CACHE.isin(id):
            print("Corpus with {0} texts \n[+\t{1}] already in cache. Loading...".format(len(paths), ',\n+\t'.join(paths)))
            return self.CACHE.cache[id]

        for file in paths:
            docs.append(self.segment_text_from_file(file))

        corpus = CorpusSM(docs)
        self.CACHE.add(corpus, id)

        return corpus
    pass
pass