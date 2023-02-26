#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''
INFORMATIONS GENERALES
=========================================================================
Cours de Python - M1 Sciences du Langage parcours Industries de la Langue
Projet de fin de semestre

INFORMATIONS SUR LE MODULE
=========================================================================
:auteur: Jérémy Bourdillat <Jeremy.Bourdillat@etu.univ-grenoble-alpes.fr>
:version: 1.0
Python ver. 3.11.1

OBSERVATIONS
=========================================================================
- order() : mieux gérer le niveau des tokens et, pourquoi pas, intégrer la tokenisation dedans
- zipf : permettre le choix d'utiliser les lemmes ou les formes, et permettre le tri en fonction des étiquettes
'''

import ast
import html
import pickle
import sys
from .tree.NodeSM import NodeSM
from .resources.NGramsSM import NGramsSM
from .resources.LexiconSM import LexiconSM
from .classification import ClassificationSM
from .tools.benchmark import timeit
import re
import os
import json
import xml.etree.ElementTree as ET
from zipfile import ZipFile, is_zipfile
import numpy as np
import copy




HIERARCHY = {'token' : '', 'clause' : ',;:', 'sentence' : '.?!', 'paragraph' : '\n'}



LexiquetoUD = {
    "ADJ" : "ADJ",
    "ADJ:dem" : "DET",
    "ADJ:ind" : "DET",
    "ADJ:int" : "DET",
    "ADJ:num" : "NUM",
    "ADJ:pos" : "DET",
    "ART:def" : "DET",
    "ART:inf" : "DET",
    "ART:ind" : "DET",
    "CON" : "CCONJ", # Problème ici, la source est moins précise que la sortie !
    "" : "SCONJ",
    "NOM" : "NOUN",
    "AUX" : "AUX",
    "PRE" : "ADP",
    "ADV" : "ADV",
    "PRO" : "PRON",
    "VER" : "VERB",
    "PRO:dem" : "PRON",
    "PRO:ind" : "PRON",
    "PRO:int" : "PRON",
    "PRO:per" : "PRON",
    "PRO:pos" : "PRON",
    "PRO:rel" : "PRON",
    "ONO" : "INTJ",
    "$" : "SYM",
    "" : "PROPN",
    "" : "PART",
    "" : "PUNCT",
    "" : "X"	
}





class SegmentedTextSM:
    '''
    Représente un texte segmenté en tokens et organisés hiérarchiquement.
    La classe donne accès à des statistiques sur le texte en lui-même, et permet des exports en tout type.
    Par la suite, elle permettra aussi d'effectuer des recherches assez précises sur les différents éléments (formes, tokens, lemmes, etc.)
    et de générer des statistiques personnalisées.

    Ainsi, l'objectif est double : 
    - Permettre l'export de différentes représentations du texte (lemmes, formes, statistiques diverses, phrases, etc.)
    - Permettre une représentation en mémoire simple et accessible pour une utilisation facile en tant que bibliothèque externe 
    '''

    grm = re.compile(r"""
    (?:etc\.|p\.ex\.|cf\.|M\.|MM\.) |
    (\w+['’]? |
    \- |
    [^\s\w]+ |
    \n) 
    """, flags=re.X)
   
    @timeit
    def __init__(self, txt: str or list, lexicon: LexiconSM, model:NGramsSM, *, doc_name: str = "", levels: dict=HIERARCHY):

        self.listObjs = []

        self.hierarchy: dict = levels

        self._index: int = 0

        self.stats: dict = {"nbChar" : 0}

        self.name = doc_name


        # Si l'on a fournit un texte d'entrée, on s'occupe de le traiter (permet de générer des objets vides)
        if txt != None:

            self.txt = txt

            self.listObjs = self._tokenize(txt, self.grm) # On tokenise le texte avec la grammaire

            if isinstance(lexicon, LexiconSM): # Si un lexique a été fourni :
                self._lexicalize(self.listObjs, lexicon)
            else:
                raise TypeError

            if isinstance(model, NGramsSM): # Si un modèle de tagging basé sur des NGrams a été fourni :
                self.lemmas = self._tag(self.listObjs, model)
                self.stats['nbLm'] = len(self.lemmas)
            else:
                raise TypeError

            self.stats["nb" + list(levels)[0]] = len(self.listObjs) # On stocke le nombre de tokens

            types = [i for i in self.listObjs if i.tags["cat"] not in ["PUNCT", "NUM", "X"]]
            self.types = ClassificationSM.DataStatsSM(types, NGramsSM(txt=types, sep=' '))

            lemmas = [i.tags['lemme'] + ':' + i.tags['cat'] for i in self.listObjs]
            self.lemmas = ClassificationSM.DataStatsSM(lemmas, NGramsSM(txt=lemmas, sep=' '))

            self.stats['types'] = len(self.types.stats['1'])
            self.stats['lemmes'] = len(self.lemmas.stats['1'])
            

            self.stats['vocCurve']: list = []
            self.stats['zipf']: list = []

            #self._order(levels) # On génère l'arbre à partir des tokens

            self._order()

            ty = set()
            cmptr = 0
            for i, t in enumerate(self.listObjs):
                
                if t.tags["cat"] not in ["PUNCT", "NUM", "X"]:
                    if t.txt not in ty:
                        cmptr += 1
                        ty.add(t.txt)

                if (i+1)%100 == 0:
                    # On crée un point dans la courbe du vocabulaire tous les 100 tokens
                    self.stats['vocCurve'].append((i+1, cmptr))

            for u in self.types.stats['1']:
                # On trie les formes par fréquence absolue dans le texte :
                self.stats['zipf'].append((u, self.types.stats['1'][u]))
                self.stats['zipf'].sort(key=lambda item : item[1], reverse=True)

            # On calcule le ratio type/token
            self.stats['typeTokenRatio'] = round(self.stats['types'] / self.stats["nb" + list(levels)[0]], 3)
    pass

    
    @timeit
    def _tokenize(self, txt: str or list, regex) -> list:
        """
        Tokenise la chaîne de caractères à l'aide d'une expression régulière.
        """

        sys.stdout.write("\nTokenisation en cours...\n")

        if not isinstance(txt, str) and iter(txt) != None:
            out = []
            cmptr = 0
            for line in txt:
                for tok in regex.findall(line):
                    if tok != '':
                        cmptr += 1
                        out += [NodeSM(tok, index=cmptr)]
                self.stats["nbChar"] += len(line)
            return out

        else:
            self.stats["nbChar"] = len(txt)
            return [NodeSM(tok, index=i) for i, tok in enumerate(regex.findall(txt)) if tok != '']
    pass

    
    @staticmethod
    @timeit
    def _lexicalize(tokens: list, lexicon: LexiconSM) -> None:
        """
        Procède à l'analyse lexicale des tokens, en déterminant toutes les possibilités de lemme à partir d'un lexique
        """

        sys.stdout.write("\nLexicalisation en cours...\n")

        # On compile les expressions régulières qui servent à reconnaître des cas particuliers (utile pour les gros fichiers)
        digits = re.compile(r"[0-9]+")
        propn = re.compile(r"[A-Z]\w+")
        punct = re.compile(r"[\W\S]+")

        
        for i, token in enumerate(tokens):

            # On teste avec deux versions : une normale et une en minuscule. L'idée est de prendre en compte les
            # noms propres d'une part, et les mots en début de phrase (donc avec majuscule) d'autre part
            versions: list = [token.txt, token.txt.lower(), token.txt[:-1] if token.txt[:-1] == "'" else token.txt, token.txt[:-1] if token.txt[:-1] == "’" else token.txt, 
                token.txt[:-1].lower() if token.txt[:-1] == "'" else token.txt.lower(), token.txt[:-1].lower() if token.txt[:-1] == "’" else token.txt.lower()] 
            tagged: bool = False

            for txt in versions:

                token.tags = []

                if txt in lexicon.lex.keys(): # Si le token est dans le lexique :
                    lemmas = lexicon[txt] # On récupère la liste des lemmes et leur catégorie
                    for j in lemmas:
                        if j["cat"] in LexiquetoUD.keys(): # Si la catégorie existe dans le tableau de conversion vers les UDs :
                            j["cat"] = LexiquetoUD[j["cat"]]
                            j["freq"] = float(j["freq"])
                            #token.tags.append({"cat" : LexiquetoUD[j["cat"]], "lemme" : j["lemme"], })
                            token.tags.append(j)
                        else:
                            j["cat"] = "X"
                            token.tags.append(j)
                    tagged = True
                    break

            if not tagged: # Si le token n'a aucune hypothèse de tag, on regarde s'il fait partie des cas particuliers
                if digits.match(token.txt) != None: # Si le token est composé de chiffres
                    token.tags = [{"lemme" : token.txt, "cat" : "NUM", "genre" : "", "nombre" : "", "freq" : np.nan}]

                elif propn.match(token.txt) != None: # Si le token commence par une majuscule, on dit que c'est un nom propre
                    token.tags = [{"lemme" : token.txt, "cat" : "PROPN", "genre" : "", "nombre" : "", "freq" : np.nan}]

                elif punct.match(token.txt) != None: # Si le token n'est ni un espace blanc, ni une lettre alors c'est une ponctuation
                    token.tags = [{"lemme" : token.txt, "cat" : "PUNCT", "genre" : "", "nombre" : "", "freq" : np.nan}]

                else:
                    token.tags = [{"lemme" : token.txt, "cat" : "X", "genre" : "", "nombre" : "", "freq" : np.nan}]

            sys.stdout.write(f"LEX\t{i+1:>8} / {len(tokens):<8} ({round(i/len(tokens)*100, 1)}%)\r")

    pass

    
    @staticmethod
    @timeit
    def _tag(tokens: list, reference: NGramsSM) -> dict:
        """
        Prend en entrée une liste de tokens analysés lexicalement et une référence (dictionnaire de n-grammes).
        Opère directement sur la liste de tokens NodeSM.
        Retourne un set des lemmes
        """

        sys.stdout.write("\nEtiquetage en cours...\n")

        # On définit une taille minimale de chaîne pour l'analyse en ngrammes
        window_min = min([int(i) for i in reference.n])

        # On crée un buffer des tokens précédents + celui courant et un sac de lemmes (pour les stats)
        buffer: list = []
        lm: dict = {}

        for i, tok in enumerate(tokens): # On parcours les tokens du texte
            buffer.append(tok)


            if len(tok.tags) > 1 and len(buffer[-window_min:]) >= window_min: 
                # Si l'on a plusieurs possibilités de lemmes et un buffer assez grand pour effectuer l'analyse en ngrammes :

                frqs: list = [] # liste des fréquences des combinaisons

                total_freq_tok = 0
                for lemma in tok.tags:
                    total_freq_tok += lemma["freq"]
                
                for lemma in tok.tags: # Pour chaque lemme possible
                    
                    # On génère une liste des catégories de la combinaison (ex : ["DET", "NOUN", "ADJ"])
                    chain = [previous.tags["cat"] for previous in buffer[-window_min:-1]] + [lemma["cat"]]

                    # Si la chaîne fait partie des ngrammes, 
                    if reference.sep.join(chain) in reference[str(len(buffer[-window_min:]))].keys():
                        frqs.append(
                            reference[str(len(buffer[-window_min:]))] # taille de ngrammes concernée
                            [reference.sep.join(chain)] # le ngramme concerné
                            / total_freq_tok
                            )
                    else:
                        frqs.append(np.nan) # Si le ngramme n'existe pas, alors on considère sa fréquence comme nulle (très peu probable)

                tok.tags = list(tok.tags)[frqs.index(max(frqs))] # On définit le lemme en prenant celui avec la plus haute fréquence 

                if tok.tags['lemme'] + ':' + tok.tags['cat'] in lm:
                    lm[tok.tags['lemme'] + ':' + tok.tags['cat']] += 1 # On ajoute le lemme à la liste des lemmes
                else:
                    lm[tok.tags['lemme'] + ':' + tok.tags['cat']] = 1

            else:
                tok.tags = list(tok.tags)[0]


            sys.stdout.write(f"TAG\t{i+1:>8} / {len(tokens):<8} ({round(i/len(tokens)*100, 1)}%)\r")

        return lm

    pass


    @timeit
    def _order(self, hierarchy: dict =HIERARCHY) -> NodeSM:
        '''
        La fonction 'order' découpe le texte tokenisé en différents niveaux imbriqués spécifiés dans 'hierarchy' et crée un arbre (non-syntaxiques)
        à partir des tokens. Elle renvoie ensuite le noeud maître, qui donne accès par le haut aux données.
        hierarchy est un dictionnaire avec le nom et les délimiteurs utilisés, ordonné depuis le plus petit ensemble. Dans la fonction,
        les niveaux sont imbriqués, c'est à dire que le niveau 5 ne peut contenir que des éléments de niveau 4, le niveau 4 des éléments de niveau
        3 etc. 
        '''

        sys.stdout.write("\nHiérarchisation en cours... \n")

        #buffer est une mémoire tampon contenant, pour chaque niveau, les différents noeuds.
        #delims est un tableau de chaînes qui contiennent les délimiteurs ; chaque niveau inférieur contient les délimiteurs du niveau supérieur afin
        # de les imbriquer.
        buffer = [[] for i in range(len(hierarchy))]
        delims = [""]*(len(hierarchy))
        self.levels: dict = {}

        #cette boucle génère les différentes chaînes de délimiteurs issus de 'hierarchy' 
        for i in range(1, len(hierarchy)):
            self.levels[list(hierarchy)[i]] = []
            temp = list(hierarchy)[i:]

            for c in temp:
                delims[i] = delims[i] + ''.join(hierarchy[c])


        for i, token in enumerate(self.listObjs):
            # On ajoute chaque token au buffer de tokens (niveau 0)
            buffer[0].append(token)

            for h,key in enumerate(hierarchy):
                # On parcourt les différents niveaux hiérarchiques pour vérifier si le token appartient à un ou plusieurs d'entre eux
                if delims[h].find(str(token)) != -1:
                    #si on trouve un démarqueur de niveau :
                    if h > 0: # On ignore le niveau des tokens (pas de segmentation à y faire)
                        phrase = NodeSM(token.txt) # On crée un noeud du niveau concerné
                        phrase.type = key
                        phrase.index = len(self.levels[key])
                        self.levels[key].append(phrase)

                        if ("nb" + key) in self.stats:
                            self.stats["nb" + key] += 1
                        else:
                            self.stats["nb" + key] = 1

                    

                    for el in buffer[h-1]: # On rattache tous les noeuds sans parents du niveau précédent au nouveau noeud
                        if el.parent == None:
                            el.relateAsChild(phrase)

                    # On ajoute ce nouveau noeud au buffer
                    buffer[h].append(phrase)
            
            sys.stdout.write(f"ORDER\t{i+1:>8} / {len(self.listObjs):<8} ({round(i/len(self.listObjs)*100, 1)}%)\r")

        # Une fois toute la structure finalisée, on crée un noeud final auquel on va raccorder tous les noeuds supérieurs
        buffer.append([NodeSM("", "texte")])


        if len(buffer[-2]) > 0:
            buffer[-1][0].groupSetParent(buffer[-2][:])
        # Si la couche la plus élevée est vide (ça arrive) alors on raccorde à celle en dessous
        else:
            buffer[-2].append(NodeSM("", list(hierarchy)[-1]))
            self.stats["nb" + list(hierarchy)[-1]] = 1
            buffer[-2][0].groupSetParent(buffer[-3][:])
            buffer[-1][0].groupSetParent(buffer[-2][:])

        self.masterNode = buffer[-1][0]

        for level in hierarchy:
            if ("nb" + level) in self.stats:
                self.stats[level[:len(level)] + "Len"] = {
                    "char" : round(self.stats['nbChar'] / self.stats["nb" + level], 2),
                    list(hierarchy)[0] : round(self.stats["nb" + list(hierarchy)[0]] / self.stats["nb" + level], 2),
                    "types" : round(self.stats['types'] / self.stats["nb" + level], 2),
                    "lemmes" : round(self.stats['lemmes'] / self.stats["nb" + level], 2)
                }
    pass

    def _order_new(self) -> NodeSM:

        levels = {
            "weak" : [",", ":", ";"],
            "strong" : [".", "?", "!"],
            "parentheses" : {"\"" : "\"", "'": "'", "«" : "»", "[" : "]", "(" : ")"}
        }

        buffer: list = []
        chunks: list = []

        masterNode: NodeSM = NodeSM("texte", "texte")

        for token in self.listObjs:
            found = ""

            for i, lvl in enumerate(levels):
                if token.txt in levels[lvl]:
                    found = lvl
                    break

            if token.tags['cat'] in ("CCONJ", "PUNCT"):

                chunks.append(buffer)
                token.type = "chunk"


                #if found == "weak":
                token.groupSetParent(buffer)
                """elif found == "strong":
                    for c in chunks:
                        for tok in c:
                            if tok.parent != None:
                                token.relateAsParent(tok.parent)
                                break
                            else:
                                token.relateAsParent(tok)"""
                chunks = []
                masterNode.relateAsParent(token)
                
                buffer = []
            else:
                buffer.append(token)           
            
        self.masterNode = masterNode
    pass


    ############################################################################################################
    #   Interactions des données
    ############################################################################################################

    def distance(self, txt) -> dict:
        return self.types.compare(self.types.stats.ngrams['1'], txt.types.stats.ngrams['1'])
    pass

    def distance_lemmas(self, txt) -> dict:
        return ClassificationSM.DataStatsSM.compare(self.lemmas.stats.ngrams['1'], txt.lemmas.stats.ngrams['1'])
    pass

    ############################################################################################################
    #   Input/Output
    ############################################################################################################

    @timeit
    def report(self, path: str = "", textname: str = "txt", zip: bool = False, graphs=False) -> None:
        """
        Exporte le texte en csv, xml et fichier binaire dans un dossier selon un nom attribué
        """

        folder = os.path.join(path, textname)

        try:
            os.mkdir(folder)
        except FileExistsError:
            sys.stdout.write(f"\nDossier \"{folder}\" existe déjà.\n")

        tsvF = os.path.join(folder, textname + ".tsv")
        xmlF = os.path.join(folder, textname + ".xml")
        smF = os.path.join(folder, textname + ".sm")
        imgVocF = os.path.join(folder, textname + "_vocab.png")
        imgZipfF = os.path.join(folder, textname + "_zipf.png")
        jsonF = os.path.join(folder, textname + "_report" + ".json")

        self.to_csv(tsvF)
        self.to_XML(xmlF)
        self.save(smF)

        with open(jsonF, mode="w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent="\t", ensure_ascii=False)

        """if graphs and 'vocCurve' in self.stats.keys():
            # On génère le graph du vocabulaire
            plt.figure(figsize=(6.4*3, 4.8*3))
            plt.plot([i[0] for i in self.stats['vocCurve']], [i[1] for i in self.stats['vocCurve']])
            plt.xlabel("tokens")
            plt.ylabel("vocabulaire")
            plt.title("Evolution du vocabulaire au fil du texte")
            plt.savefig(imgVocF)
            plt.clf()

        if graphs and 'zipf' in self.stats.keys():
            # On génère le graph des fréquences de formes

            zipf = [i for i in self.stats['zipf'] if i[1] > 1]
            
            zipf = zipf[:100]
            plt.figure(figsize=(6.4*3, 4.8*3))
            plt.plot([i[0] for i in zipf], [i[1] for i in zipf])
            plt.xlabel("types")
            plt.xticks(rotation=90)
            plt.ylabel("fréquence")
            plt.title("Types en fonction de leur fréquence")
            plt.savefig(imgZipfF)"""

        if zip:
            # On enregistre le tout dans une archive zip
            with ZipFile(textname + ".zip", mode="w") as zipO:
                zipO.write(tsvF)
                zipO.write(xmlF)
                zipO.write(smF)
                zipO.write(imgVocF)
                zipO.write(imgZipfF)
                zipO.write(jsonF)
    pass


    def serialize(self) -> str:
        """
        
        """

        linear: dict = {}
        for i, token in enumerate(self.listObjs):
            tags = {"text" : token.txt}
            tags.update(token.tags)
            linear[str(i)] = tags

        tree: dict = self.to_XML()

        return json.dumps({"linear" : linear, "tree" : tree, "stats" : self.stats}, ensure_ascii=False)

    pass

    def to_csv(self, filename: str = None) -> None:
        """
        Exporte les tokens avec leurs tags dans un fichier tabulé
        """

        out: str = list(self.hierarchy)[0] + '\t' + '\t'.join(self.listObjs[0].tags.keys()) + '\n'

        for token in self.listObjs:
            if token.txt not in ('\n', '\t', '\r'):
                if isinstance(token.tags, list):
                    out += str(token) + "\t" + '\t'.join(token.tags) + '\n'
                elif isinstance(token.tags, dict):
                    out += str(token) + "\t" + '\t'.join([str(token.tags[i]) for i in token.tags]) + '\n'

        if filename != None:
            with open(filename, mode="w", encoding="utf-8") as f:
                f.write(out)

        return out
    pass


    def to_XML(self, filename: str = None) -> None or str:
        """
        Exporte l'arbre du texte dans un fichier xml.
        """
        if filename != None:
            file = open(filename, mode="wb")

        top = ET.Element('SegmentedTextSM')
        XMLTree = ET.ElementTree(top)

        #if self.hierarchy != None:
        #    top.set("hierarchy", self.hierarchy)

        if self.name != "":
            top.set("name", self.name)

        def parseChildren(node: NodeSM, parent):
            for child in node.children:
                ch = ET.SubElement(parent, child.type)

                for tag in child.tags:
                    ch.set(tag, str(child.tags[tag]))

                #ch.set("struct", child.struct)

                if child.type == list(self.hierarchy)[0]:
                    if child.txt in ['\n', '\r', '\t']:
                        ch.text = repr(child.txt)
                        continue
                    else:
                        ch.text = child.txt
                else:
                    ch.set("token", child.txt)

                parseChildren(child, ch)
        pass

        parseChildren(self.masterNode, top)

        #ET.indent(XMLTree, "    ")

        if filename and file:
            XMLTree.write(file, encoding='utf-8', xml_declaration=True)
            file.close()
        else:
            return ET.tostring(XMLTree.getroot(), encoding="unicode", method='xml')
            
    pass

    @classmethod
    def from_xml(cls, filename):
        """
        Importe un fichier XML contenant un texte SegmentedTextSM
        /!\ Les statistiques n'étant pas contenues dans le XML, elles ne seront pas importées ! /!\\
        """

        with open(filename, mode='rb') as file:
            tree = ET.parse(file)
            root = tree.getroot()


            levels: dict = ast.literal_eval(root.get('hierarchy'))
            name = root.get("name")
            tokens: list[str] = []
            masterNode: NodeSM = NodeSM()


            def parseChildren(node: ET.Element, dataParent: NodeSM):

                for child in node:

                    if child.tag == list(levels)[0]:
                        if child.text in ['\n', '\r', '\t']:
                            wrd = NodeSM(text=str(ast.literal_eval("'" + child.text + "'")))
                        else:
                            wrd = NodeSM(text=child.text)
                        tokens.append(wrd)
                    else:
                        wrd = NodeSM(text=child.text)
                    
                    wrd.tags: dict = {}
                    for attr in child.items():
                        wrd.tags[attr[0]] = attr[1]

                    wrd.type = child.tag
                    
                    dataParent.relateAsParent(wrd, topLevel=True, replace=True)
                    parseChildren(child, wrd)

            parseChildren(root, masterNode)

            txt = cls(levels=levels)
            txt.listObjs = tokens
            txt.masterNode = masterNode
            txt.name = name

            return txt

    pass

    def save(self, filename: str) -> None:
        """
        Sauvegarde un fichier binaire contenant un objet "SegmentedTextSM"
        """

        with open(filename, mode="wb") as file:
            pickle.dump(self, file)
    pass

    @classmethod
    def load(cls, filename: str):
        """
        Charge un fichier binaire contenant un objet "SegmentedTextSM", ou une archive contenant ce fichier
        """
        if is_zipfile(filename):
            with ZipFile(filename, mode="r") as zipO:
                with zipO.open(filename.split(".")[-2] + "/" + filename.split(".")[-2] + ".sm", mode="r") as file:
                    obj = pickle.load(file)
        else:
            with open(filename, mode="rb") as file:
                obj = pickle.load(file)

        if isinstance(obj, cls):
            return obj
        else:
            raise TypeError
    pass


    ############################################################################################################
    #   Dunders et recherche
    ############################################################################################################

    def __add__(self, seg2): # Nécessite d'être retravaillé

        newData = SegmentedTextSM()

        newData.hierarchy = self.hierarchy
        newData.lemmas = self.lemmas | seg2.lemmas
        newData.listObjs = self.listObjs + seg2.listObjs
        newData.types = self.types | seg2.types

        newData.masterNode = NodeSM(type="texte")
        newData.masterNode.children = self.masterNode.children + seg2.masterNode.children

        for key in self.stats:
            newData.stats[key] = self.stats[key]

        for key in seg2.stats:
            if key in newData.stats.keys():
                newData.stats[key] += seg2.stats[key]
            else:
                newData.stats[key] = seg2.stats[key]

        return newData
    pass


    def __str__(self) -> str:

        return " ".join([str(i) for i in self.listObjs])
    pass

    def __len__(self) -> int:
        return len(self.listObjs)
    pass

    def __iter__(self):
        self._index = 0
        return self
    pass

    def __next__(self):
        if self._index < len(self.listObjs):
            result = str(self.listObjs[self._index])
            self._index += 1
            return result
        raise StopIteration
    pass

    def __hash__(self) -> int:
        return self.txt.__hash__()
    pass


    ############################################################################################################
    #   Recherche (WIP zone, réalisé avant et nécessitant d'être retravaillé)
    ############################################################################################################

    def remove(self, item):
        if not item in self:
            raise ValueError

        if isinstance(item, NodeSM):
            self.listObjs.remove(item)
        elif isinstance(item, str):
            for obj in self.listObjs:
                if item == str(obj):
                    self.listObjs.remove(obj)
    pass

    def hasInSuccession(self, needle: NodeSM) -> bool:
        listWords: list = self.getListWords()
        i: int = 0
        indices: list = []
        has: bool = True

        if not isinstance(needle, list):
            return True

        while i < self.getNbWords():
            for ne in needle:                
                if len(ne) == str(listWords[i]):
                    indices.append(needle.index(ne))
                    needle.remove(ne)
            if len(needle) == 0:
                break
            i += 1

        for i in indices:
            if i>0 and indices[i]-1 == indices[i-1]:
                has = True
            else:
                return False

        return has
    pass

    def has(self, needle: NodeSM) -> bool:
        '''Retourne si oui ou non, le texte possède le mot ou la liste de mots en entrée. Les mots de la liste sont testés \
            de manière discontinue (=non contigue)'''
        
        i: int = 0

        if isinstance(needle, list):
            for i in range(0, len(self)):
                for ne in needle:
                    if isinstance(ne, list):
                            if self.hasInSuccession(ne):
                                needle.remove(ne)
                    else:
                        if str(ne) == str(self.listObjs[i]):
                            needle.remove(ne)
                if len(needle) == 0:
                    break

        else:
            for i in range(0, len(self)):
                if str(needle) == str(self.listObjs[i]):
                    needle = []

        if len(needle) > 0:
            return False
        else:
            return True
    pass



    def findIndex(self, needle: NodeSM) -> tuple:
        '''Trouve le premier index des mots recherchés. Les index sont retournés dans l'ordre croissant (pas l'ordre des mots).'''

        result: tuple(int,) = ()
        if isinstance(needle, list):
            for i in range(0, len(self)):
                for ne in needle:
                    if isinstance(ne, list):
                            if self.hasInSuccession(ne):
                                result += (i,)
                    else:
                        if str(ne) == str(self.listObjs[i]):
                            result += (i,)
                if len(needle) == 0:
                    break
            return result
        else:
            for i in range(0, len(self)):
                if needle == str(self.listObjs[i]):
                    return (i,)

        return (-1,)
    pass


    def retrieve(self, needle):
        
        listWords = self.getListWords()

        '''for i in range(0, self.getNbWords()):
            if needle == listWords[i].getString():
                return listWords[i]
        return None'''

        i = 0

        while i < self.getNbWords():# and needle != listWords[i].getString():
            if needle == listWords[i].getString():
                return listWords[i]
            else:
                i += 1

        return None
    pass

    def search_seq(self, seq):

        ind_seq = 0
        for i in range(len(self.listObjs)):
            if len(seq) <= len(self.listObjs)-i:
                if seq[ind_seq] == self.listObjs[i].getString():
                    ind_seq += 1
                    if ind_seq == len(seq):
                        return i-len(seq)+1
                else:
                    ind_seq = 0
            else:
                return -1

    pass
        


###################################################################################################################################################

