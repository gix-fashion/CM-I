#!/usr/bin/python3

"""
Used to process the datas, extract the keywords and etc.

Composed by Zhand Danyang @THU
"""

import csv

import sys
sys.path.insert(0, "../..")

import utils
import re
import itertools

files = ["2015版药典中药功效大全.new.csv", "中国中草药配伍大全.csv", "中药学表格.csv"]

with open("中药数据库.csv") as f:
    reader = csv.DictReader(f)
    std_names = [[utils.remove_white_spaces(r["药名"])] + [utils.remove_white_spaces(m) for m in re.split(r"[、,，。. 　]+", r["别名"])] for r in reader]
    #std_names = itertools.chain.from_iterable(std_names)
    #std_names = list(std_names)
    std_names = [set(g) for g in std_names]

#names = []
#for fn in files[:-1]:
    #with open(fn) as f:
        #reader = csv.reader(f)
        #names.append([r[0] for r in reader])
#
#with open(files[-1]) as f:
    #reader = csv.DictReader(f)
    #names.append([r["药名"] for r in reader])

#for ns in names:
    #print(len(ns))
#
#print()

## use names[1] as standard version
#for n in names[1]:
    ##if n not in names[1]:
    #if n not in std_names:
        #print(n)
        ##for sn in names[1]:
        #for sn in std_names:
            #if utils.is_identical(n, sn):
                #print("\t" + sn)

diff_libs = [
        "2015版药典中药功效大全_未匹配目录_std",
        "中国中草药配伍大全_未匹配目录_std",
        "中药学表格_未匹配目录_std"
]

special_policies = []
for dl in diff_libs:
    with open(dl) as f:
        recipes = (l.strip() for l in f)
        recipes = (l.split() for l in recipes)
        recipes = (set(l) for l in recipes)
        special_policies += recipes

for nns in special_policies:
    matched = False
    for ens in std_names:
        if len(ens & nns)>0:
            ens |= nns
            matched = True
    if not matched:
        std_names.append(nns)

std_names = [" ".join(sorted(ns)).strip() for ns in std_names]
for ns in std_names:
    print(ns)
