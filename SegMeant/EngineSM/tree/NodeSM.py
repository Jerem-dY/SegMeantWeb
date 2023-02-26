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
- revoir les fonctions d'encapsulation et de désencapsulation
'''

import json

class NodeSM:
    def __init__(self, text: str="", type: str="token", index=0):
        self.parent: NodeSM = None
        self.ind: int = 0
        self.children: list = []
        self.tags: list = []
        self.struct: str = ""
        self.txt = text
        self.type = type
        self.index = index
    pass

    @classmethod
    def from_list(cls, ls: list) -> list:
        """
        Prend une liste de chaines de caractères et retourne une liste d'objets NodeSM
        """
        return [cls(el) for el in ls]
    pass

    def toJSON(self):
        s = ""
        s += json.dumps(self.txt, indent='\t', ensure_ascii=False)
        s += json.dumps(self.tags, indent='\t', ensure_ascii=False)

        for el in self.children:
            s += json.dumps(el.toJSON(), indent='\t', ensure_ascii=False)

        return s
    pass

    def __iter__(self):
        self.current_index: int = 0
        return self
    pass

    def __len__(self):
        return len(self.children)
    pass

    def __next__(self):
        if self.current_index < len(self.children):
            x = self.children[self.current_index]
            self.current_index += 1
            return x
        raise StopIteration
    pass

    def __getitem__(self, item):
        return self.children[item]
    pass

    def __str__(self):
        s: list = [self.txt] if self.txt != '' else []
        for child in self.children:
            s.append(repr(child)[1:-1])
        return ' '.join(s)
    pass

    def __repr__(self):
        return repr(self.txt)
    pass

    def isType(self, nodeType):
        return isinstance(self, nodeType)
    pass

    def relateAsParent(self, child, topLevel=True, replace=False):
        if replace or self.parent == None:
            child.ind = len(self.children)
            self.children.append(child)
            if topLevel:
                child.relateAsChild(self, False)
    pass

    def relateAsChild(self, parent, topLevel=True):
        self.parent = parent
        if topLevel:
            parent.relateAsParent(self, False)
    pass

    def next(self, iter=0):
        if self.parent != None and len(self.parent.children) > self.ind+1+iter :
            return self.parent.children[self.ind+1+iter]
        
        return None
    pass

    def previous(self, iter=0):
        if self.parent != None and self.ind-1+iter>=0:
            return self.parent.children[self.ind-1+iter]

        return None

    def delRelations(self):
        del self.parent
        del self.ind
        del self.children

        NodeSM.__init__(self)
    pass

    """def set_tags(self, tg: str):

        args = tg.split("+")
        for a in args:
            if "=" in a:
                members = a.split("=")
                self.add_tag(members[0], members[1])
            else:
                self.add_tag(a, None)
    pass"""

    def decapsulate(self):
        #sert à récupérer l'enfant qui est le plus en bout d'arbre (=pas d'enfants)
        r = []

        if len(self.children)>0:
            

            for child in self.children:
                
                if len(child.children)>0:
                    r = r + child.decapsulate()
                    
                else:
                    r.append(child)
                    #print(len(r), r[-1])
        else:
            r = self

        return r
    pass


    def getDepth(self):
        r = []
        count = 1

        if len(self.children)>0:
            

            for child in self.children:
                
                if len(child.children)>0:
                    r = r + child.decapsulate()
                    
                else:
                    r.append(child)
                    count += 1
                    #print(len(r), r[-1])
        else:
            r = self

        return count
    pass


    def decapsulateToType(self, childType):
        #sert à récupérer le noeud le plus bas d'un certains type
        r = self

        if len(self.children)>0:
            if isinstance(self.children[0], childType):
                r = self.children[0]
            else:
                for child in self.children:
                    r = child.decapsulateToType(childType)

        else: 
            return None

        return r
    
    pass

    ###############

    def encapsulate(self):
        #sert à récupérer le parent des noeuds (parent commun)

        if self.parent != None:
                r = self.parent.encapsulate()
        else:
                r = self

        return r
    pass

    def groupSetParent(self, nodes):
        for n in nodes:
            self.relateAsParent(n)
    pass
pass


class LeafSM(NodeSM):

    def __init__(self, text: str="", type: str="token", index: int=0):
        super().__init__(text, type, index)
        del self.children
    pass
pass