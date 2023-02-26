# -*- coding: utf-8 -*-

import numpy as np
from dataclasses import dataclass


distance_methods: set = {
    'dice',
    'jaccard',
    'cos',
    'coefCorrel',
    'coefLin',
    'coefVar'
}




def dice(size_a:int, size_b:int, intersection:list) -> float:
    '''Retourne l'indice DICE de similarité entre les deux listes :
    s(t1, t2) = 2(t1 ∩ t2) / (|t1| + |t2|)
    Avec t1 et t2 débarassés des doublons
    '''

    if size_a+size_b != 0:
        return (2*intersection)/(size_a+size_b)
    else:
        return 0

pass

def jaccard(size_a:list, size_b:list, intersection:list) -> float:
    '''Retourne l'indice jaccard de similarité entre les deux listes :
    J(t1, t2) = (t1 ∩ t2) / (t1 ∪ t2)
    Avec t1 et t2 débarassés des doublons
    '''
    if (size_a+size_b-intersection) != 0:
        return intersection/(size_a+size_b-intersection)
    else:
        return 0

pass

def cosVector(vec1: np.ndarray, vec2: np.ndarray) -> float:
    '''Retourne le cosinus des deux vecteurs de taille égale générés depuis les deux textes étudiés.
    cos(v1, v2) = (v1 ∙ v2) / (∥v1∥ * ∥v2∥) = pdtScalaire(v1, v2) / pdtNormes(v1, v2)
    '''

    v1norm = 0
    v2norm = 0

    #On calcule la norme de chaque vecteur, en élevant chaque coordonée au carré pour ensuite faire la racine de la somme, 
    # afin d'obtenir la valeur absolue
    for val in vec1:
        v1norm += val*val

    for val in vec2:
        v2norm += val*val
    
    v1norm = np.sqrt(v1norm)
    v2norm = np.sqrt(v2norm)

    #On calcule le produit scalaire (la somme du produit des coordonnées des vecteurs deux à deux)
    scalarProduct = 0
    for i in range(0, len(vec1)):
        scalarProduct += (vec1[i]*vec2[i])

    if (v1norm*v2norm) != 0:
        return scalarProduct / (v1norm*v2norm)
    else:
        return 0
pass

def correlation(vec1: np.ndarray, vec2: np.ndarray) -> float:
    
    if len(vec1) == 0 or len(vec2) == 0:
        return 0
    
    mean1: float = np.sum(vec1)/len(vec1)
    mean2: float = np.sum(vec2)/len(vec2)

    ecart1: np.ndarray = np.full(len(vec1), np.nan)
    for i, v in enumerate(vec1):
        ecart1[i] = v - mean1

    ecart2: np.ndarray = np.full(len(vec2), np.nan)
    for i, v in enumerate(vec2):
        ecart2[i] = v - mean2
    
    sumP = 0
    for i in range(len(vec1)):
        sumP += ecart1[i]*ecart2[i]

    s1 = 0
    for e in ecart1:
        s1 += e ** 2

    s2 = 0
    for e in ecart2:
        s2 += e ** 2

    denom = np.sqrt((s1) * (s2))

    if denom == 0:
        return 0

    return sumP / denom

pass

def linCoef(x: list, y: list):

    down = (variance(x) + variance(y) + ((np.sum(x)/len(x)) - (np.sum(y)/len(y))) ** 2)

    if down == 0:
        return 0

    up = (2*coVar(x, y))
    

    return up / down
pass

def coVar(x: np.ndarray, y: np.ndarray):
    
    mean1: float = np.sum(x)/len(x)
    mean2: float = np.sum(y)/len(y)

    ecart1: np.ndarray = np.full(len(x), np.nan)
    for i, v in enumerate(x):
        ecart1[i] = v - mean1

    ecart2: np.ndarray = np.full(len(y), np.nan)
    for i, y in enumerate(y):
        ecart2[i] = v - mean2
    
    sumP = 0
    for i in range(len(x)):
        sumP += ecart1[i]*ecart2[i]


    return sumP/len(x)
pass

def variance(x: np.ndarray):
    mean: float = np.sum(x)/len(x)

    ecart: np.ndarray = np.full(len(x), np.nan)
    for i, v in enumerate(x):
        ecart[i] = v - mean
    
    sumP = 0
    for i in range(len(x)):
        sumP += ecart[i] ** 2


    return sumP/len(x)
pass


def extr_matrice(mat: np.ndarray) -> dict:
    """
    Extrait les extrema de la matrice (min et max) et renvoit leurs coordonnées sous la forme d'un dictionnaire.

    Entrées :
    -   mat : matrice de réels

    Sorties :
    -   dictionnaire à deux clés : 'min' : (x, y), 'max': (x, y)
        +   x et y sont les coordonnées de la valeur dans la matrice
    """

    row_max = 0
    row_min = 0

    extr_max = None
    extr_min = None

    # Ligne par ligne, on cherche l'extremum et on le compare au précédent ; s'il est plus extrême encore, on le remplace
    for col in range(0, len(mat)):
        row_max = np.nanmax(mat[col])
        row_min = np.nanmin(mat[col])

        if extr_max == None or row_max > extr_max:
            extr_max = row_max
            out_max = (col, mat[col].index(extr_max))
            

        if extr_min == None or row_min < extr_min:
            extr_min = row_min
            out_min = (col, mat[col].index(extr_min))
            
    print(f"{out_min}:{extr_min}", f"{out_max}:{extr_max}")

    return {"min" : out_min, "max": out_max}
pass



def compare(vector1: dict, vector2: dict) -> dict:


    intersection = vector1.keys() & vector2.keys()

    v1: np.ndarray = np.full(len(intersection), np.nan)
    v2: np.ndarray = np.full(len(intersection), np.nan)

    out: dict = {}

    for i, key in enumerate(intersection):
        v1[i] = vector1[key]
        v2[i] = vector2[key]

        #print(f"{i} / {len(intersection)}")

    out['dice'] = dice(len(vector1), len(vector2), len(intersection))
    out['jaccard'] = jaccard(len(vector1), len(vector2), len(intersection))
    out['cos'] = cosVector(v1, v2)
    out['coefCorrel'] = correlation(v1, v2)
    out['coefLin'] = linCoef(v1, v2)
    out['coefVar'] = cosVector(v1, v2)

    return out
pass


def dist_matrix(elements: list, method: str = None) -> dict:

    size: int = len(elements)
    mats: dict = {}

    for m in distance_methods:
        mats[m]: np.ndarray = np.full((size-1, size), np.nan)

    for i in range(size-1):
        for j in range(size):
            if j > i:
                comp = compare(elements[i], elements[j])

                for m in comp:
                    mats[m][i][j] = comp[m]


    return mats
pass



@dataclass
class DataStatsSM:
    data: list
    stats: dict

    """def compare(self, vector2) -> dict:
        return super().compare(self.stats, vector2.stats)
    pass"""
pass
