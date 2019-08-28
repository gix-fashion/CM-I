#!/usr/bin/python3

"""
Extract pathogenisis keywords.

Composed by Zhand Danyang @THU
"""

import sys
sys.path.insert(0, "../..")

import json

import itertools
import utils

with open("中医常见病症.json") as f:
    database = json.load(f)["常见病"]
    database = ((set(utils.extract_equivalent_expressions(k)), w["子类"]) for k, w in database.items() if "子类" in w)
    database = itertools.chain.from_iterable(((k, w) for w in sub) for k, sub in database)
    database = (w["性质"] for _, w in database if "性质" in w)

with open("中华人民共和国中医药行业标准-中医证候诊断标准16.json") as f:
    database2 = json.load(f).values()
    database2 = itertools.chain.from_iterable(database2)
    database2 = itertools.chain.from_iterable(w["症候分类"].keys() for w in database2 if "症候分类" in w)
    #database2 = itertools.chain.from_iterable(w["病症"].keys() for w in database2)

database = itertools.chain(database, database2)
database = set(database)

for kw in database:
    print(kw)
