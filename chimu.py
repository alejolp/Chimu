#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import string
import pprint


WHITESPACE = " \t\r\n"
NEWLINE = "\r\n"
NAMECHARSTART = set(string.ascii_letters)
NAMECHAR = NAMECHARSTART | set(string.digits + "_")

"""
S: ['fragment'] name ':' B ';'
T: name | ['~'] '[' text ']' | '{' text '}' ['?'] | '\'' text '\'' | '"' text '"'
B: E ( '|' E )*
E: T | '(' B ')' | E '*' | E '+' | E '?'
"""

def parse(toks):
    i = 0
    d = {'grammar': None, 
        'options': {},
        'tokens': [],
        'ats': [],
        'tree': {}}
    while i < len(toks):
        # print i, toks[i], toks[i-10:i+10]
        if toks[i] == 'grammar':
            # grammar X ;
            d['grammar'] = toks[i+1]
            assert toks[i+2] == ';'
            i += 3
        elif toks[i] == 'options':
            # options { language = Java ; }
            assert toks[i+1] == '{'
            i += 2
            while i < len(toks) and toks[i] != '}':
                assert toks[i+1] == '=' and toks[i+3] == ';'
                d['options'][toks[i]] = toks[i+2]
                i += 4
            i += 1
        elif toks[i] == 'tokens':
            # tokens { A, B }
            assert toks[i+1] == '{'
            i += 2
            while i < len(toks) and toks[i] != '}':
                d['tokens'].append(toks[i])
                if toks[i+1] == ',':
                    i += 2
            i += 1
        elif toks[i] == '@':
            # @ parser :: members { ... }
            assert toks[i+4] == '{' and toks[i+6] == '}'
            d['ats'].append((toks[i:i+4], toks[i+5]))
            i += 7
        else:
            # normal production
            # e : e | e ;
            # fragment e : e | e ;

            isfragment = (toks[i] == 'fragment')
            if isfragment:
                name = toks[i]
                assert toks[i+2] == ':'
            else:
                name = toks[i]
                assert toks[i+1] == ':'
            k = i
            while k < len(toks) and toks[k] != ';':
                k += 1
            assert toks[k] == ';'
            i = k + 1
    return d

def tokenize(S):
    i = 0
    a = 0
    toks = []
    while i < len(S):
        # print i, S[i], S[i-10:i+10]
        if S[i:i+2] == '/*':
            while i < len(S) and S[i:i+2] != '*/':
                i += 1
            i += 2
        elif S[i] in WHITESPACE:
            i += 1
        elif S[i:i+2] == '//' or S[i] == '#':
            while i < len(S) and S[i] not in NEWLINE:
                i += 1
        elif S[i] in NAMECHARSTART:
            a = i
            while i < len(S) and S[i] in NAMECHAR:
                i += 1
            toks.append(S[a:i])
        elif S[i:i+2] in ['::', '->']:
            toks.append(S[i:i+2])
            i += 2
        elif S[i] in [':', ';', '|', '(', ')', '?', '+', '*', '~', '.', '@', '=', ';', '}']:
            toks.append(S[i])
            i += 1
        elif S[i] in ['"', "'"]:
            q = S[i]
            a = i
            i += 1
            while i < len(S) and S[i] != q:
                if S[i] == '\\':
                    i += 2
                else:
                    i = i + 1
            toks.append(S[a:i+1])
            i += 1
        elif S[i] == '[':
            a = i
            while i < len(S) and S[i] != ']':
                if S[i] == '\\':
                    i += 2
                else:
                    i += 1
            toks.append(S[a])
            toks.append(S[a+1:i])
            toks.append(S[i])
            i += 1
        elif S[i] == '{':
            if (len(toks) > 0 and toks[-1] == 'options'):
                toks.append(S[i])
                i += 1
                continue

            a = i
            toks.append(S[i])
            i += 1
            stack = ['{']
            while i < len(S) and len(stack) > 0:
                if S[i:i+2] == '//' or S[i] == '#':
                    while i < len(S) and S[i] not in NEWLINE:
                        i += 1
                    i += 1
                elif S[i:i+2] == '/*':
                    while i < len(S) and S[i:i+2] != '*/':
                        i += 1
                    i += 2
                elif S[i] == '{':
                    stack.append('{')
                    i += 1
                elif S[i] == '}':
                    e = stack.pop(-1)
                    assert e == '{'
                    i += 1
                else:
                    i += 1
            toks.append(S[a+1:i-1])
            toks.append(S[i-1])
        else:
            print i, S[i], repr(S[i-10:i+10])
            assert False
    return toks

def main():
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        #fname = "C://Users//ale//Documents//GitHub//grammars-v4//c//C.g4"
        fname = "C://Users//ale//Documents//GitHub//grammars-v4//ecmascript//ECMAScript.g4"
        #fname = "C://Users//ale//Documents//GitHub//grammars-v4//vb6//VisualBasic6.g4"

    with open(fname, 'r') as f:
        toks = tokenize(f.read())
    pprint.pprint(toks)

    tree = parse(toks)
    pprint.pprint(tree)

if __name__ == '__main__':
    main()
