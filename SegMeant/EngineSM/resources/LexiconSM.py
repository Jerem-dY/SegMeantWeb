#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''
INFORMATIONS GENERALES
=========================================================================
Cours de Python - M1 Sciences du Langage parcours Industries de la Langue
Devoir Maison à rendre pour le 05 Décembre 2022

INFORMATIONS SUR LE MODULE
=========================================================================
:auteur: Jérémy Bourdillat <Jeremy.Bourdillat@etu.univ-grenoble-alpes.fr>
:version: 1.2
Python ver. 3.10.7


CHANGELOG
=========================================================================
    >   Ajout de la prise en compte des potentiels doublons de couple (peu de chance que ça arrive 
        puisque le fichier n'en contient normalement pas, mais sait-on jamais).
    >   Compilation de la regex pour des questions de performances futures.
    >   Suppression  de la première ligne, qui ne contient que les en-têtes de colonne
    >   Ajout des fonctions to_json() et from_json() pour exporter/importer le lexique en json (permettant
        de le recharger en mémoire pour une autre utilisation)
    >   Conversion des fréquences en nombre pour pouvoir trier correctement !

OBSERVATIONS
=========================================================================
Possibles améliorations :
    >   Accès aux formes : créer un système de noeud qui concrétise les lemmes, et permette ainsi d'accéder aux autres formes possibles
        d'un même lemme et leurs informations.
    >   Générisation de l'expression régulière : permettre à l'utilisateur de choisir lui-même les colonnes qui l'intéressent,
        et ainsi permettre une plus grande flexibilité d'utilisation. (problèmes actuels : "catastrophic backtracking" car trop 
        de quantifieurs imbriqués quand tentative de factoriser l'expression) Solution : passer par un système plus simple qui récupère toutes
        les valeurs (via un .split() par exemple) puis offrir le choix des colonnes via une liste d'indices.
    >   Framework : lier ce module aux autres développés dans le cadre du cours ; permettre une interopérabilité des différents outils.

Notes :
    >   Il a été décidé d'intégrer la fréquence du lemme dans les livres dans la structure de données, et ce pour deux raisons :
        +   D'abord, cela évite d'avoir à stocker cette information à part pour la jeter une fois le tri fait (ce serait du gâchis)
        +   Ensuite, il peut être utile de conserver cette information pour permettre à l'utilisateur de trier d'une manière différente sans
            que cela ne soit destructeur (= perte de l'ordre original), par exemple en exportant les données ciblées dans un fichier tabulé 
            (plus lisible que le gros lexique).
    >   Bien que dans l'énoncé il soit indiqué des couples [catégorie, lemme], le choix a été fait de garder l'ordre naturel du fichier lexique
        [lemme, catégorie] afin de simplifier le code et de récupérer directement le dictionnaire obtenu via l'expression régulière. A noter que
        changer l'ordre est faisable assez facilement, mais non sans répercussions possibles sur l'évolutivité :
        +   On peut copier dans un nouveau dictionnaire les clés du couple dans le désordre (sachant qu'en python, l'ordre des clés est
            garanti être celui d'ajout). Problème : si l'on souhaite ajouter de nouvelles infos à la structure, cela nécessite de réadapter le code
            pour les prendre en compte et déterminer leur place.
        +   On peut modifier le comportement de l'export : en effet, puisque nos couples sont des dictionnaires, certes l'ordre est garanti mais en théorie
            celui-ci n'est pas censé être le plus utilisé, l'avantage du tableau associatif étant d'avoir un accès en O(1) grâce à une clé-objet. Ainsi, si
            l'on souhaite un affichage ou un export selon un certain ordre il suffit d'utiliser les bonnes clés dans le bon ordre, ce que peut même déterminer 
            l'utilisateur en passant par exemple une liste de clés ordonnée à une fonction prévue à cet effet : ['cat', 'lemme']
'''

import re
import json
import shelve
import pandas as pd


##########################################################################################################
# DEFINITIONS                                                                                            #
##########################################################################################################

class LexiconSM:
    """
    Représente un lexique de formes auxquelles sont associés des lemmes, POS et fréquences.

    Le lexique est un dictionnaire des formes, auxquelles sont associés une liste des différents couples cat/lemme et leur fréquence
    sous la forme, là aussi, de dictionnaires pour faciliter l'accès aux données. 
    Par défaut, les couples sont classés par fréquence décroissante.
    """

    # L'expression régulière qui permet de récupérer les informations qui nous intéressent 
    # (certes, peu évolutif ; c'edt vraiment histoire de s'amuser)
    regex = re.compile(
    r"""
    (?P<forme>[^\n\t]*) # on récupère la forme
    \t
    [^\n\t]* # on ignore la colonne de phonétique
    \t 
    (?P<lemme>[^\n\t]*) # on récupère le lemme (3e colonne)
    \t
    (?P<cat>[^\n\t]*) # on récupère la catégorie (4e colonne)
    \t
    ([^\n\t]*\t){3} # on ignore les colonnes qui ne nous intéressent pas
    (?P<freq>[^\n\t]*) # on récupère la fréquence (8e colonne)
    """, flags=re.U | re.X)


    def __init__(self, shelf=""):

        if shelve != "":
            self.lex = shelve.open(shelf, writeback=False)
        else:

            self.lex = {}

        
    pass

    @classmethod
    def create(cls, dico_file_name:str, *, sort="freq", shelf="SegMeant/EngineSM/resources/lexicon/lexicon"):
        """lit le fichier ligne par ligne, récupère les informations pertinentes et construit la structure de données."""

        lexicon = cls(shelf)



        if dico_file_name != "":

            columns = ["ortho", "lemme", "cgram", "genre", "nombre", "freqlemlivres"]
            dico = pd.read_table("SegMeant/EngineSM/resources/Lexique383.tsv", usecols=columns)
            
            for row in dico.itertuples():
                
                freq = float(getattr(row, "freqlemlivres"))
                forme = getattr(row, "ortho")

                if pd.notna(forme):
                    d = {"lemme" : getattr(row, "lemme"), "cat" : getattr(row, "cgram"), "genre" : getattr(row, "genre") if pd.notna(getattr(row, "genre")) else "", "nombre" : getattr(row, "nombre") if pd.notna(getattr(row, "nombre")) else "", sort : getattr(row, "freqlemlivres")}

                    if forme in lexicon.lex:
                        tk = lexicon.lex[forme]

                        if  d not in tk:
                                    tk.append(d) # Si la clé est déjà présente dans le lexique mais que le couple n'existe pas pour cette forme, alors on rajoute le couple à la liste associée
                                    lexicon.lex[forme] = tk
                    else:
                        lexicon.lex[forme] = [d]

            """with open(dico_file_name, mode="r", encoding="utf-8") as f:

                f.readline() # On supprime les en-têtes de colonne en faisant avancer le curseur à la ligne suivante

                for line in f: # On parcourt ligne par ligne le fichier, pour éviter de charger en mémoire un fichier potentiellement gigantesque

                    row = LexiconSM.regex.match(line)

                    d = row.groupdict() # On récupère un dictionnaire des groupes nommés
                    key = d.pop("forme") # On récupère la forme et on l'enlève du dictionnaire (elle va constituer la clé dans notre lexique)

                    d[sort] = float(d[sort]) # On convertit la fréquence en un nombre décimal, pour pouvoir classer par la suite

                    if key in lexicon.lex:
                        tk = lexicon.lex[key] #On stocke une copie de l'objet (obligatoire avec shelve sans writeback)
                        if  d not in tk:
                            tk.append(d) # Si la clé est déjà présente dans le lexique mais que le couple n'existe pas pour cette forme, alors on rajoute le couple à la liste associée
                            lexicon.lex[key] = tk
                    else:
                        lexicon.lex[key] = [d]"""


            for form in lexicon.lex: # Pour chaque forme, on trie ses couples de valeurs selon l'un des attributs (par défaut, la fréquence)
                lexicon.lex[form].sort(key= lambda couple : couple[sort], reverse=True)

        return lexicon
    pass

    def attr_val(self, form: str, attr: str) -> list:
        """Retourne la liste des différentes valeurs possibles pour l'attribut demandé ('lemme', 'cat' ou 'freq')"""

        results = []
        for couple in self.lex[form]:
            results.append(couple[attr])

        return results
    pass

    def __iter__(self):
        """Rend itérable l'objet sur son attribut lex (pour récupérer chaque forme et ses couples une par une)"""
        return iter(self.lex)
    pass

    def __del__(self):
        if isinstance(self.lex, shelve.Shelf):
            self.lex.close()
    pass

    def __getitem__(self, key):
        """Permet de récupérer les valeurs d'une forme particulière"""
        return self.lex[key]
    pass

    def to_json(self, fname: str):
        """Enregistre le lexique dans le fichier json spécifié"""

        with open(fname, mode="w", encoding="utf-8") as f:
            json.dump(dict(self.lex), f, indent="\t", ensure_ascii=False)
    pass

    @staticmethod
    def from_json(fname):
        """Importe un lexique enregistré en json."""

        lex = LexiconSM("")
        with open(fname, mode="r", encoding="utf-8") as f:
            lex.lex = json.load(f)

        return lex
    pass

    @classmethod
    def load(cls, shelve="SegMeant/data/lexicon/lexicon"):
        return cls(shelve)
    pass


pass



##########################################################################################################
# UTILISATION (tests)                                                                                    #
##########################################################################################################

if __name__ == "__main__":

    #lex = LexiconSM.create("Lexique/Lexique383.tsv") # On crée le lexique en transmettant un nom de fichier TSV
    lex = LexiconSM.load()
    lex.to_json("resources/test.json") # On exporte le lexique en .json

    """print(lex["abrité"]) # On affiche l'ensemble des couples associés à la forme "abrité"
    print(lex.attr_val("abrité", "lemme")) # On utilise la méthode 'attr_val' pour récupérer la valeur d'un attribut pour une forme donnée


    lex = Lexicon.from_json("test.json") # Permet de récupérer le lexique 

    for el in lex:
        print(el, lex[el]) # On affiche chaque forme avec ses couples de valeurs"""

