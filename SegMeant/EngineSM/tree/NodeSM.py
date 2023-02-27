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
    """
    Classe pouvant représenter diverses unités linguistiques avec pour point commun la possibilité de former un arbre, permettant de former différentes représentations des éléments de la langue écrite.

    :param text: la forme graphique portée par le noeud
    :type text: str
    :param type: le type de noeud (arbitraire, décidé par l'utilisateur)
    :type type: str
    :param index: un index pour positionner le noeud sur un seul axe (utile pour la sérialisation)
    :type idnex: int
    """


    def __init__(self, text: str = "", type: str = "token", index=0):
        """
        Constructeur de la classe.
        """

        self.parent: NodeSM = None
        self.ind: int = 0
        self.children: list = []
        self.tags: list = {}
        self.struct: str = ""
        self.txt = text
        self.type = type
        self.index = index
    pass

    @classmethod
    def from_list(cls, ls: list, indexify: bool = False, start_index: int = 0) -> list:
        """
        Méthode de classe prenant une liste de chaines de caractères et retournant une liste d'objets NodeSM.

        :param ls: liste des éléments à transformer en noeuds
        :type ls: liste de str
        :param indexify: détermine si l'on souhaite indexer les noeuds les uns par rapport aux autres
        :type indexify: bool
        :param start_index: l'index de départ
        :type start_index: int
        :return: liste de noeuds
        :rtype: liste de :class:`NodeSM`
        """

        if indexify:
            return [cls(el, index=i) for i, el in enumerate(ls, start=start_index)]
        else:
            return [cls(el) for el in ls]
    pass

    def toJSON(self, indent='\t') -> str:
        """
        Sérialise récursivement le noeud et ses enfants sous la forme d'une chaîne de caractère formattée en JSON.

        :param indent: Défini le(s) caractère(s) utilisé(s) pour indenter les éléments et rendre le tout plus lisible pour l'être humain (déconseillé pour être lu par une machine)
        :type indent: str
        :return: la chaîne au format JSON
        :rtype: str
        """

        s = ""
        s += json.dumps(self.txt, indent=indent, ensure_ascii=False)
        s += json.dumps(self.tags, indent=indent, ensure_ascii=False)

        for el in self.children:
            s += json.dumps(el.toJSON(indent), indent=indent, ensure_ascii=False)

        return s
    pass

    def relateAsParent(self, child, topLevel: bool = True, replace: bool = False) -> None:
        """
        Défini le noeud courant comme étant le parent de celui passé en argument. Le paramètre "replace" permet de définir si l'on force le remplacement du parent ou non.

        :param child: Le noeud que l'on souhaite définir comme enfant
        :type child: :class:`NodeSM`
        :param topLevel: Quand topLevel est activé, cela signifie que l'objet passé en argument va lui aussi être modifié à l'aide de la méthode complémentaire (ici, relateAsChild()), celle-ci
        n'étant alors obligatoirement pas topLevel
        :type topLevel: bool
        :param replace: Défini si l'on doit forcer le remplacement du parent précédent de l'enfant
        :type replace: bool
        """

        if replace or self.parent == None:
            child.ind = len(self.children)
            self.children.append(child)
            if topLevel:
                child.relateAsChild(self, False)
    pass

    def relateAsChild(self, parent, topLevel: bool = True) -> None:
        """
        Défini le noeud courant comme étant l'enfant de celui passé en argument.

        :param parent: Le noeud que l'on souhaite définir comme parent
        :type parent: :class:`NodeSM`
        :param topLevel: Quand topLevel est activé, cela signifie que l'objet passé en argument va lui aussi être modifié à l'aide de la méthode complémentaire (ici, relateAsParent()), celle-ci n'étant alors obligatoirement pas topLevel
        :type topLevel: bool
        """

        self.parent = parent
        if topLevel:
            parent.relateAsParent(self, False)
    pass

    def groupSetParent(self, nodes: list) -> None:
        """
        Permet de définir le noeud courant comme étant le parent d'une liste de noeuds, et ce de manière non-destructive (si un noeud a déjà un parent, il le garde).

        :param nodes: la liste des noeuds a modifier
        :type nodes: une liste de :class:`NodeSM`
        """

        for n in nodes:
            self.relateAsParent(n)
    pass

    def next(self, iter: int = 0):
        """
        Permet un parcours horizontal de l'arbre sur le même niveau, en récupérant le prochain noeud enfant du même parent.

        :param iter: de combien d'enfants l'on souhaite avancer
        :type iter: int
        :return: le noeud demandé
        :rtype: :class:`NodeSM`
        """

        if self.parent != None and len(self.parent.children) > self.ind+1+iter :
            return self.parent.children[self.ind+1+iter]
        
        return None
    pass

    def previous(self, iter: int = 0):
        """
        Permet un parcours horizontal de l'arbre sur le même niveau, en récupérant le précédent noeud enfant du même parent.

        :param iter: de combien d'enfants l'on souhaite reculer
        :type iter: int
        :return: le noeud demandé
        :rtype: :class:`NodeSM`
        """

        if self.parent != None and self.ind-1+iter>=0:
            return self.parent.children[self.ind-1+iter]

        return None

    def delRelations(self) -> None:
        """
        Réinitialise toutes les relations du noeud, en le faisant aussi oublier des autres (cela peut entraîner la perte des noeuds sans aucune autre référence).
        """

        del self.parent.children[self.ind]
        del self.parent
        del self.ind

        for c in self.children:
            del c.parent
            del c
    pass


    def decapsulate(self) -> list:
        """
        Récupère la liste des feuilles (noeuds terminaux) accessibles depuis ce noeud.

        :return: l'ensemble des feuilles auxquelles a accès le noeud.
        :rtype: liste de :class:`NodeSM`
        """
        
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

    def decapsulateToType(self, childType: str):
        """
        Récupère la première feuille du type demandé.

        :param childType: le type voulu (arbitraire)
        :type childType: str
        :return: la feuille du type voulu
        :rtype: :class:`NodeSM` ou None
        """

        r = self

        if len(self.children)>0:
            if self.children[0].type == childType:
                r = self.children[0]
            else:
                for child in self.children:
                    r = child.decapsulateToType(childType)

        else: 
            return None

        return r
    
    pass

    def encapsulate(self):
        """
        Récupère le plus haut parent dans l'arbre commun aux noeuds parcourus.

        :return: le noeud le plus haut
        :rtype: :class:`NodeSM` ou None
        """

        if self.parent != None:
                r = self.parent.encapsulate()
        else:
                r = self

        return r
    pass

    def getDepth(self) -> int:
        """
        Compte le nombre de niveaux qui séparent ce noeud de la première feuille rencontrée.

        :return: Le nombre de niveaux encore en dessous.
        :rtype: int
        """

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



    ###############################################################################
    # DUNDER METHODS
    ###############################################################################


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
pass
    
