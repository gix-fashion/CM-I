#!/usr/bin/python3

"""
Make a contrast between the following three databases.

Composed by Zhand Danyang @THU
"""

ctlg1 = "2015版药典中药功效大全.new.csv" #catalogue 1: drug encyclopaedia
ctlg2 = "中国中草药配伍大全.csv" #catalogue 2: encyclopaedia of medicinal material compatibility
ctlg3 = "中药学表格.csv" #catalogue3: drug table

import csv
import json
import pickle as pkl

import sys
sys.path.insert(0, "../..")

import utils
import re

utils.special_identical_names = [
        ("芒硝", "玄明粉"),
        ("木蝴蝶", "千层纸")
]
utils.special_different_names = [
        ("五味子", "五倍子"),
        ("紫珠叶", "紫苏叶"),
        ("紫苏叶", "苏子"),
        ("冬瓜子", "南瓜子"),
        ("冬瓜子", "冬葵子"),
        ("冬葵子", "天葵子"),
        ("天葵子", "天仙子"),
        ("地耳草", "地锦草"),
        ("苎麻根", "蓖麻根", "茼麻子", "亚麻子"),
        ("草乌", "川乌"),
        ("药子", "芥子", "附子")
]

if __name__ == "__main__":
    with open(ctlg1) as f:
        reader = csv.reader(f)
        records1 = list(reader)
        # 2 columns: 药名, 功效
    with open(ctlg2) as f:
        reader = csv.reader(f)
        records2 = list(reader)
        # 3 columns: 药名, 典型方（有空）, 功效
    with open(ctlg3) as f:
        reader = csv.DictReader(f)
        records3 = list(reader)
        # keys: 药名, 性味, 功效, 临床应用

    fused_drugs = []
    # elements in it: dict like 
    # {
    #   "id": <int>,
    #   "药名": set(<str>),
    #   "性味": set(<str>),
    #   "功效": [<str>, <str>, <str>],
    #   "典型方": set(<str>),
    #   "临床应用": [<str>, ...]
    # }
    for d in records1:
        #print(d)
        d[0] = utils.remove_white_spaces(d[0])
        exists_identical = False
        for ed in fused_drugs:
            if utils.is_identical_for_iterable(d[0], ed["药名"]):
                ed["药名"].add(d[0])
                ed["功效"].append(d[1].strip())
                exists_identical = True
                break
        if not exists_identical:
            fused_drugs.append({
                "id": len(fused_drugs),
                "药名": set((d[0],)),
                "性味": set(),
                "功效": [d[1].strip()],
                "临床应用": []
            })
    for d in records2:
        d[0] = utils.remove_white_spaces(d[0])
        exists_identical = False
        for ed in fused_drugs:
            if utils.is_identical_for_iterable(d[0], ed["药名"]):
                ed["药名"].add(d[0])
                ed["功效"].append(d[2].strip())
                if d[1].strip()!="":
                    if "典型方" not in ed:
                        ed["典型方"] = set()
                    ed["典型方"].add(d[1].strip())
                exists_identical = True
                break
        if not exists_identical:
            fused_drugs.append({
                "id": len(fused_drugs),
                "药名": set((d[0],)),
                "性味": set(),
                "功效": [d[2].strip()],
                "临床应用": []
            })
            if d[1].strip()!="":
                fused_drugs[-1]["典型方"] = set((d[1].strip(),))
    for d in records3:
        d["药名"] = utils.remove_white_spaces(d["药名"])
        for ed in fused_drugs:
            if utils.is_identical_for_iterable(d["药名"], ed["药名"]):
                ed["药名"].add(d["药名"])
                ed["功效"].append(d["功效"].strip())
                ed["性味"].add(d["性味"].strip())
                ed["临床应用"] += utils.divide_into_sentences(d["临床应用"])
                exists_identical = True
                break
        if not exists_identical:
            fused_drugs.append({
                "id": len(fused_drugs),
                "药名": set((d["药名"],)),
                "性味": set((d["性味"].strip(),)),
                "功效": [d["功效"].strip()],
                "临床应用": utils.divide_into_sentences(d["临床应用"])
            })

    for d in fused_drugs:
        d["药名"] = list(d["药名"])
        d["性味"] = list(d["性味"])
        if "典型方" in d:
            d["典型方"] = list(d["典型方"])
    try:
        with open("融合中药药性库.json", "wt") as f:
            json.dump({"database": fused_drugs}, f, indent="\t", ensure_ascii=False)
    except:
        with open("融合中药药性库.pkl", "wb") as f:
            pkl.dump({"database": fused_drugs}, f)

    #for d in drugs1 + drugs2 + drugs3:
        #exists_identical = False
        #for ed in fused_drugs:
            #if utils.is_identical_for_iterable(d, ed[1:]):
                #ed.append(d)
                #exists_identical = True
                #break
        #if not exists_identical:
            #fused_drugs.append([len(fused_drugs), d])
    #for d in fused_drugs:
        #print(str(d[0]) + "\t\t" + "\t\t".join(d[1:]))
