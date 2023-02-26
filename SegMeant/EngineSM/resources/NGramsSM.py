#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''
INFORMATIONS GENERALES
=========================================================================
Cours d'algorithmique - M1 Sciences du Langage parcours Industries de la Langue
Devoir Maison à rendre pour le 30 novembre 2022

INFORMATIONS SUR LE MODULE
=========================================================================
:auteur: Jérémy Bourdillat <Jeremy.Bourdillat@etu.univ-grenoble-alpes.fr>
:version: 1.0
Python ver. 3.10.7

OBSERVATIONS
=========================================================================
Utilisation de générateurs difficile à rendre sous forme de pseudocode.
'''

import shelve
import copy
import re




class NGramsSM:
    """
    Cette classe représente un texte découpé en n-grammes, qui peuvent être récupérés en format tableur ou sous la forme d'un dictionnaire
    """

    stop_list: list = [".", ",", ";", ":", "!", "?", "\t", "\n", "\r"]

    def __init__(self, *, n: set = {1, 2, 3}, sep: str = '', dic: dict = None, txt: str = None):
        """Constructeur. Analyse le texte selon une liste de tailles de n-grammes spécifiée."""

        self.ngrams: dict = {}

        if dic != None and len(dic) > 0:
            self.n = list(dic.keys())
        else:
            self.n = set(n)


        self.sep = sep

        if dic != None:
            self.ngrams = dic

            if len(dic) > 0:
                return
            
        
        # On vérifie que les tailles de n-grammes entrées sont valides (entre 0 et 20, et seulement des entiers)   
        for el in n:
            if not isinstance(el, int):
                raise TypeError
            if el <= 0 or el > 20:
                raise ValueError

        if isinstance(txt, str):
            txt = txt.lower() # On met tout en minuscule pour éviter les doublons "Et" / "et" liés aux majuscules

            for punc in self.stop_list: # On supprime la ponctuation du texte
                txt = txt.replace(punc, "")
            
            txt = list(txt)

        
        buffer: list = []

        for level in self.n: # Pour chaque taille de n-grammes
            self.ngrams[str(level)] = {}
            ngramsBuf = {}
            for k in txt:
                buffer.append(str(k)) # On ajoute le caractère courant au buffer

                if len(buffer) == level: # Si l'on a atteint la bonne taille de n, soit on ajoute le n-gramme au dictionnaire s'il n'y est pas, sinon on incrémente son nombre d'occurences
                    nb = sep.join(buffer)
                    if nb in ngramsBuf:
                        ngramsBuf[nb] += 1
                    else:
                        ngramsBuf[nb] = 1
                    
                    # On décale la fenêtre de 1 caractère ; cela permet aussi de remettre à zéro le buffer en fin de chaîne : 
                    # sélectionner une portion qui n'existe pas ne renvoie pas d'erreur, mais une chaîne vide. Pratique !
                    buffer = buffer[1:] 
            self.ngrams[str(level)] = ngramsBuf


    pass

    def relative_frequency(self) -> dict:

        output = {}
        # Pour chaque n-gramme référencé, on remplace comme valeur la simple fréquence absolue par un dictionnaire contenant la fréquence absolue ET la fréquence relative que l'on calcule
        for lvl in self.ngrams.keys():
            tmp = copy.deepcopy(self.ngrams[lvl])
            for k in tmp.keys():
                freq = tmp[k]
                tmp[k] = round((freq / len(self.ngrams[lvl]))*100, 4)

            output[lvl] = dict(sorted(sorted(list(tmp.items())), key=len, reverse=True)) # On trie les clés selon leur taille et l'ordre alphabétique

        return output
    pass

    def __del__(self):
        if isinstance(self.ngrams, shelve.Shelf):
            self.ngrams.close()
    pass

    def __iter__(self):
        return iter(self.ngrams)

    def __getitem__(self, key):
        return self.ngrams[key]
    pass

    def _projection(self, d: dict, print_keys: bool = True, print_children_keys: bool = False) -> list:
        """
        Générateur qui projette l'arborescence de données sur une liste d'une seule dimension, 
        pouvant optionnellement contenir les identifieurs de chaque couple clé valeur.
        """

        row: list = []

        for key in d:
            if print_keys: # si l'on a demandé à inclure les clés elles-mêmes dans la liste
                row = [key]
            else:
                row = []
            try: # on vérifie si la valeur associée à la clé est un objet itérable.
                iter(d[key])

                # Si c'est le cas, on va chercher récursivement les valeurs de chaque élément
                for val in self._projection(d[key], print_children_keys, print_children_keys):
                    row += val
            except TypeError:
                # Sinon on ajoute normalement la valeur à la liste
                row.append(d[key])
            yield row # A chaque itération, on renvoie la projection d'un élément et de ses valeurs

    pass

    def _to_row(self, sep='\t') -> str:
        """Générateur qui retourne une chaîne représentant une ligne de tableau, adaptée à l'export en CSV ou TSV"""

        # Pour chaque n-gramme dont les données sont ramenées sur une seule ligne, 
        # on génère une chaîne de caractère des valeurs séparées par un séparateur.
        for lvl in self.ngrams:
            for line in self._projection(self.ngrams[lvl]):
                yield sep.join(str(item) for item in line)
    pass


    def format(self, headers: list = [], sep='\t', newline='\n') -> str:
        """Fonction qui génère le contenu d'un fichier tableur"""

        if len(headers) > 0:
            out: str = sep.join(headers) + newline
        else:
            out: str = ""

        for i in self._to_row(sep):
            out += i + newline

        return out

    pass
pass


def extractNgrams(input_file: str, output_file: str) -> None:
    with open(input_file, mode="r", encoding="utf-8") as in_f:
        ngrammes = NGramsSM.create(in_f.read(), n=range(1, 4))

    with open(output_file, mode="w", encoding="utf-8") as out_f:
        out_f.write(ngrammes.format(["ngram", "frequency"]))
pass


if __name__ == "__main__":

    n = extractNgrams("grosTxt.txt", "resources/markovian/fichierbidon.tsv")
    #a = NGramsSM.load("ngrams")
    print("")


