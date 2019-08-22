#!/usr/bin/python3

"""
Used to process the datas, extract the keywords and etc.

Composed by Zhand Danyang @THU
"""

import json

import sys
sys.path.insert(0, "../..")
sys.path.append("../../catalogs/病症")

import itertools
import utils
#from check_iou import DiseaseName

with open("常见病汇总.json") as f:
    baseline = itertools.chain.from_iterable(json.load(f).values())
    baseline = itertools.chain.from_iterable(utils.extract_equivalent_expressions(n) for n in baseline)
    baseline = list(baseline)
    #print(baseline)

paedias = [None for _ in range(3)]
with open("全面!114种常见疾病联合用药方案大全.json") as f:
    dict1 = json.load(f).keys()
    paedias[0] = [set(utils.extract_equivalent_expressions(n)) for n in dict1]
    #print(paedias[0])

with open("常见疾病典型病症资料.json") as f:
    dict2 = json.load(f)
    dict2 = (d.keys() for d in dict2.values())
    paedias[1] = [set(utils.extract_equivalent_expressions(n)) for n in itertools.chain.from_iterable(dict2)]
    #print(paedias[1])

with open("中医常见病症.json") as f:
    dict3 = json.load(f)["常见病"].keys()
    paedias[2] = [set(utils.extract_equivalent_expressions(n)) for n in dict3]
    #print(paedias[2])

#for n in paedias[2]:
    #if n not in baseline:
        #print(n)
        #for bn in baseline:
            #if utils.is_identical(n, bn):
                #print("\t" + bn)

diff_libs = [
        "常见疾病典型病症资料_未匹配关键词",
        "全面!114种常见疾病联合用药方案大全_未匹配关键词",
        "中医常见病症_未匹配关键词"
]

special_policies = paedias[0] + paedias[1] + paedias[2]
for l in diff_libs:
    with open(l) as f:
        dl = (line.strip() for line in f)
        dl = (set(line.split()) for line in f)
        special_policies += dl

name_set = set(baseline)
name_set = [{n.strip()} for n in baseline]
for nns in special_policies:
    matched = False
    for ens in name_set:
        if len(nns & ens)>0:
            ens |= nns
            matched = True
    if not matched:
        name_set.append(nns)

name_set = set(" ".join(sorted(s)) for s in name_set)
for s in name_set:
    print(s)
