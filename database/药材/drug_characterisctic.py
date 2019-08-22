#!/usr/bin/python3

"""
Used to process the datas, extract the keywords w.r.t. characteristic (性味) and application point (归经) of drugs and etc.

Composed by Zhand Danyang @THU
"""

import json
import csv

import sys
sys.path.insert(0, "../..")

import re
import itertools
import utils

#jsons = [
csvs = [
        "中药数据库.csv",
        "中药学表格.csv"
]

split_pat = re.compile(r"[、,，。. 　;；]+")

features = []
application_points = []

with open(csvs[0]) as f:
    reader = csv.DictReader(f)
    reader = list(reader)

    ft = (r["性味"].strip() for r in reader)
    ft = (r for r in ft if r!="")
    ft = ((utils.remove_white_spaces(ch) for ch in split_pat.split(r)) for r in ft)
    ft = itertools.chain.from_iterable(ft)
    ft = (re.sub(r"[性味有]", "", r) for r in ft)
    ft = (r for r in ft if r!="")
    features.append(ft)

    ap = (r["归经"].strip() for r in reader)
    ap = (r for r in ap if r!="")
    ap = (r[:-1] if r.endswith("经") else r for r in ap)
    ap = (r[1:] if r.startswith("归") or r.startswith("入") else r for r in ap)
    ap = ((utils.remove_white_spaces(og) for og in split_pat.split(r)) for r in ap)
    ap = itertools.chain.from_iterable(ap)
    ap = (r for r in ap if r!="")
    application_points.append(ap)

with open(csvs[1]) as f:
    reader = csv.DictReader(f)
    ft = (r["性味"].strip() for r in reader)
    ft = (r for r in ft if r!="")
    mat = (re.match(r"(.+?)(([肺肝肾心脏脾胃胆]|膀胱|[大小]?肠|三焦|[、,，。. 　;；])*)", r)
            for r in ft)
    mat = (m.group(1, 2) for m in mat)
    mat = list(mat)

    ft = (m[0] for m in mat)
    ft = (m.strip() for m in ft)
    ft = (m for m in ft if m!="")
    ft = ((utils.remove_white_spaces(ch) for ch in split_pat.split(m)) for m in ft)
    ft = itertools.chain.from_iterable(ft)
    ft = (re.sub(r"[性味有]", "", m) for m in ft)
    ft = (m for m in ft if m!="")
    features.append(ft)

    ap = (m[1] for m in mat)
    ap = (m.strip() for m in ap)
    ap = (m for m in ap if m!="")
    ap = (re.findall(r"[肺肝肾心脏脾胃胆]|膀胱|[大小]?肠|三焦", m) for m in ap)
    ap = itertools.chain.from_iterable(ap)
    ap = (m for m in ap if m!="")
    application_points.append(ap)

features = itertools.chain.from_iterable(features)
application_points = itertools.chain.from_iterable(application_points)

#with open("药性列表", "w") as f:
    #for ft in features:
        #f.write(ft + "\n")
#
#with open("归经列表", "w") as f:
    #for ap in application_points:
        #f.write(ap + "\n")

features_stat = {}
for ft in features:
    if ft not in features_stat:
        features_stat[ft] = 0
    features_stat[ft] += 1
features_stat = sorted(features_stat.items(), key=(lambda it: it[1]), reverse=True)
with open("药性列表", "w") as f:
    for ft in features_stat:
        f.write("{:}\t{:d}\n".format(ft[0], ft[1]))

application_points_stat = {}
for ap in application_points:
    if ap not in application_points_stat:
        application_points_stat[ap] = 0
    application_points_stat[ap] += 1
application_points_stat = sorted(application_points_stat.items(), key=(lambda it: it[1]), reverse=True)
with open("归经列表", "w") as f:
    for ap in application_points_stat:
        f.write("{:}\t{:d}\n".format(ap[0], ap[1]))
