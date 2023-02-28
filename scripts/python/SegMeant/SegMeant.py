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

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
LEXICON_PATH = os.path.join(DIR_PATH, "data/lexicon/lexicon")
MODEL_PATH = os.path.join(DIR_PATH, "data/tagsStats/ngrams")


class SegMeant:
    """
    Classe représentant le moteur du module. La création d'une instance permet la mise en place des ressources nécessaires aux traitements ainsi que l'accès à des Factories pour construire des corpus
    et des textes traités très facilement.
    """

    def __init__(self):
        """
        Constructeur de la classe.
        """

        self.LEXICON = LexiconSM(LEXICON_PATH)
        
        #self.CACHE = CacheSM()

        shelf = shelve.open(MODEL_PATH, writeback=False)

        if len(shelf) > 0:
            self.MODEL = NGramsSM(dic=shelf, n={2, 3, 4}, sep='+')
        else:
            with open("SegMeant/EngineSM/resources/fr_ftb-ud-train.conllu", mode="r", encoding="utf-8") as f:
                pg = ""
                ph = []
                for line in f:
                    pg += line
                    #if line == "\n":
                    ph += [el[1] for el in catGet.findall(pg) if el[1]]
                    pg = ""
                    
            self.MODEL = NGramsSM(dic=shelf, n={2, 3, 4}, sep='+', txt=ph)
    pass

    def segment_text_from_file(self, path: str) -> SegmentedTextSM:
        """
        Factory method permettant la création d'un texte tokenisé à partir d'un nom de fichier, en prenant en charge l'ajout au cache du module pour faciliter la réutilisation des données.
        
        :param path: le chemin d'accès du fichier (relatif ou absolu)
        :type path: une chaîne de caractère, de préférence en utf-8
        :return: un objet :class:`SegmentedTextSM` représentant le texte tokenisé et étiqueté.
        :rtype: une référence sur un objet :class:`SegmentedTextSM`
        """

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
        """
        Une factory générant un corpus, soit un objet rassemblant plusieurs :class:`SegmentedTextSM` et permettant des traitement de groupe, notamment des calculs de similarité et des processus
        de classification automatiques.

        :param paths: les chemins d'accès des différents fichiers textes bruts
        :type paths: une liste de chaînes de caractères
        :return: un objet :class:`CorpusSM` contenant les textes tokenisés et étiquetés
        :rtype: :class:`CorpusSM`
        """

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