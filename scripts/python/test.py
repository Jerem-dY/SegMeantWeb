#!/usr/bin/env python
# -*- coding: utf-8 -*-


from SegMeant.SegMeant import SegmentedTextSM, SegMeant
import argparse
import sys
import os
import html


if __name__ == "__main__":


    argparser = argparse.ArgumentParser(description="Analyse la similarité de deux fichiers textes.")
    argparser.add_argument('input', help="Le texte à tokeniser.", type=str, default=[""], nargs='+')
    args = argparser.parse_args()

    text: str = args.input[0]

    output = sys.stdout
    f = open(os.devnull, 'w')
    sys.stdout = f

    sm = SegMeant()


    doc = SegmentedTextSM(text, doc_name="test", lexicon=sm.LEXICON, model=sm.MODEL)

    sys.stdout = output
    f.close()
    
    """for i, token in enumerate(doc.listObjs):
        print(f"{i}: {token.txt}\t{token.tags}<br>")"""
    
    print(doc.serialize())

    
    