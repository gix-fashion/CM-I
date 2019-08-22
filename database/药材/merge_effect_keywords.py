#!/usr/bin/python3

"""
Used to process the datas, merge the keywords w.r.t. the effect of drugs with the same meaning and etc.

Composed by Zhand Danyang @THU
"""

import itertools

with open("功效关键词") as f:
    n = list(f)

n = (l.strip().split() for l in n)
n = itertools.chain.from_iterable(n)
n = sorted(n, key=(lambda it: it[1:]))
for i in n:
    print(i)
