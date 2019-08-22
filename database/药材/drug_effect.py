#!/usr/bin/python3

"""
Used to process the datas, extract the keywords w.r.t. the effect of drugs and etc.

Composed by Zhand Danyang @THU
"""

import json
import csv

import sys
sys.path.insert(0, "../..")

import itertools
import utils
import jieba

csvs = [
        "2015版药典中药功效大全.new.csv",
        "中药学表格.csv",
        "中药数据库.csv"
]
jsons = [
        "../方剂/常用中药方剂.json",
        "../方剂/中药配方大全.json"
]

effects = []
with open(csvs[0]) as f:
    reader = csv.reader(f)
    reader = list(reader)
    efs = (r[1] for r in reader)
    effects.append(efs)

with open(csvs[1]) as f:
    reader = csv.DictReader(f)
    reader = list(reader)
    efs = (r["功效"] for r in reader)
    effects.append(efs)

with open(csvs[2]) as f:
    reader = csv.DictReader(f)
    reader = list(reader)
    efs = (r["功效"] for r in reader)
    effects.append(efs)

with open(jsons[0]) as f:
    database = json.load(f).values()
    database = itertools.chain.from_iterable(db.values() for db in database)
    database = itertools.chain.from_iterable(database)
    efs = (db["功用"] for db in database if "功用" in db)
    efs = (utils.divide_into_sentences(db) for db in efs)
    efs = itertools.chain.from_iterable(efs)
    efs = (db.split("：")[0] for db in efs)
    effects.append(efs)

with open(jsons[1]) as f:
    database = json.load(f)
    database = (db[1] for db in database.items() if db[0]!="药物药性疗效表" and db[0]!="祖传秘方")
    database = itertools.chain.from_iterable(database)
    database = (db["药物功效"] for db in database if "药物功效" in db)
    effects.append(database)

effects = itertools.chain.from_iterable(effects)
#for ef in effects:
    #print(ef)

with open("药材关键词") as f:
    exclusion = list(f)
    exclusion = (l.strip() for l in exclusion)
    exclusion = (l.split()[1:] for l in exclusion)
    exclusion = itertools.chain.from_iterable(exclusion)
    #exclusion = list(exclusion)
with open("药性关键词") as f:
    ex2 = list(f)
    ex2 = (l.strip() for l in ex2)
with open("归经关键词") as f:
    ex3 = list(f)
    ex3 = (l.strip() for l in ex3)

exclusion = list(itertools.chain(exclusion, ex2, ex3))

words = (jieba.cut(s) for s in effects)
words = itertools.chain.from_iterable(words)
words = (w for w in words if w not in exclusion)
words = (w for w in words if w not in ",，.。;；:：()（）?？")
words = (w for w in words if w not in "的不你我他她好以额要能可是否哈嗯、")
words = (w for w in words if len(w)>1)

#for w in words:
    #print(w)

keyword_stat = {}
for w in words:
    if w not in keyword_stat:
        keyword_stat[w] = 0
    keyword_stat[w] += 1
with open("功效统计列表", "w") as f:
    for w, c in sorted(keyword_stat.items(), key=(lambda it: it[1]), reverse=True):
        f.write("{:}\t{:d}\n".format(w, c))
