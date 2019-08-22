#!/usr/bin/python3

"""
Used to process the datas, extract the keywords and etc.

Composed by Zhand Danyang @THU
"""

import json

import sys
sys.path.insert(0, "../..")

import utils

# unique our keywords

files = [
        "http:%%zhongyaofangji.com%all.html's_recipe_list",
        "中药配方.json",
        "中药配方大全.json",
        "常用中药方剂.json"
]

with open(files[0]) as f:
    recipe_names = list(f)
    recipe_names = (l.strip() for l in recipe_names)
    recipe_names = (l.split("/") for l in recipe_names)
    recipe_names = (set(l) for l in recipe_names)
    recipe_names = list(recipe_names)

#for rg in recipe_names:
    #print(" ".join(rg))

#database = [None]
#for fn in files[1:]:
    #with open(fn) as f:
        ##print(fn)
        #database.append(json.load(f))
#
#keywords = [[] for _ in range(3)]
## check the keywords
## for database[1]
#for ctg in database[1]:
    ##print(type(database[1][ctg]))
    #keywords[0] += (r["方剂名"] for r in database[1][ctg])
## all -> list
## this file may be dropped, for the keywords in it seem to be so unreliable
#
## for database[2]
#for ctg in database[2]:
    #if ctg=="药物药性疗效表" or ctg=="祖传秘方":
        #continue
    ##print(type(database[2][ctg]))
    #keywords[1] += (r["方剂名"] for r in database[2][ctg])
## all -> list
#
## for database[3]
#for ctg in database[3]:
    ##print(type(database[3][ctg]))
    #for sub_ctg in database[3][ctg]:
        #keywords[2] += (r["方剂名"] for r in database[3][ctg][sub_ctg])
## all -> dict
#
#for k in keywords[2]:
    #if k not in recipe_names:
        #print(k)
        #for sk in recipe_names:
            #if utils.is_identical(k, sk):
                #print("\t{:}".format(sk))

diff_libs = [
        "常用中药方剂_未匹配药品目录",
        "中药配方大全_未匹配药品目录"
]

special_policies = []
for dl in diff_libs:
    with open(dl) as f:
        sp = (l.strip() for l in f)
        sp = (l.split() for l in sp)
        sp = (set(l) for l in sp)
        sp = list(sp)
        special_policies += sp

#for sp in special_policies:
    #print(sp)

for nns in special_policies:
    matched = False
    for ens in recipe_names:
        if len(nns & ens)>0:
            ens |= nns
            matched = True
    if not matched:
        recipe_names.append(nns)

recipe_names = [" ".join(sorted(s)) for s in recipe_names]
for s in recipe_names:
    print(s)
