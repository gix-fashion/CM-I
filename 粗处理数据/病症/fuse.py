#!/usr/bin/python3

"""
Try to fuse the three databases with accordance to the considered standard one (常见病汇总.json).

Composed by Zhand Danyang @THU
"""

import sys
sys.path.insert(0, "../../")

import utils
import json
import itertools
import copy

def find_disease(name, database):
    for d in database:
        names = utils.extract_equivalent_expressions(d)
        if name in names:
            yield database[d]

with open("常见病汇总.json") as f:
    baseline = json.load(f)

with open("全面!114种常见疾病联合用药方案大全.json") as f:
    dict1 = json.load(f)

with open("常见疾病典型病症资料.json") as f:
    dict2 = json.load(f)
    dict2 = (d.items() for d in dict2.values())
    dict2 = dict(itertools.chain.from_iterable(dict2))

with open("中医常见病症.json") as f:
    dict3 = json.load(f)["常见病"]

fusion = {}
# fusion: {
#   <catagory>: {
#       <disease>: {
#           "西药方案": [
#               {
#                   "症状": [<str>, ...],
#                   "代表药物": <recipe>,
#                   "联合用药": [
#                       <recipe>,
#                       ...
#                   ],
#                   "说明": [<str>, ...],
#                   "配伍原因": [<str>, ...]
#               },
#               ...
#           ],
#           "中药方案": [
#               {
#                   "病机": [<str>, ...],
#                   "子类": [
#                       {
#                           "性质": <str>,
#                           "对策": <str>,
#                           "给方": [<str>, ...]
#                       },
#                       ...
#                   ]|"子类": {
#                       <subcatagory>: [
#                           {
#                               "性质": <str>,
#                               "对策": <str>,
#                               "给方": [<str>, ...]
#                           },
#                           ...
#                       ],
#                       ...
#                   },
#                   "治疗原则": [<str>, ...],
#                   "牵引治疗": [<str>, ...]
#               },
#               ...
#           ]
#       },
#       ...
#   },
#   ...
# }
for catag in baseline:
    curr_list = {}
    fusion[catag] = curr_list
    for disease in baseline[catag]:
        curr_disease = {"西药方案": [], "中药方案": []}
        curr_list[disease] = curr_disease

        # for dict1
        for i in find_disease(disease, dict1):
            j = copy.copy(i)
            j["联合用药"] = j.pop("组方")
            curr_disease["西药方案"].append(j)

        # for dict2
        for i in find_disease(disease, dict2):
            for symptom in i:
                s = copy.copy(symptom)
                s["联合用药"] = []
                if "用药方案1" in s:
                    s["联合用药"].append(utils.format_recipe_from_str_to_list(s.pop("用药方案1")))
                if "用药方案2" in s:
                    s["联合用药"].append(utils.format_recipe_from_str_to_list(s.pop("用药方案2")))
                s["症状"] = utils.divide_into_sentences(s["症状"])
                if "代表药物" in s:
                    s["代表药物"] = utils.format_recipe_from_str_to_list(s["代表药物"])
                curr_disease["西药方案"].append(s)

        # for dict3
        for i in find_disease(disease, dict3):
            j = copy.copy(i)
            if "病机" in j:
                j["病机"] = utils.divide_into_sentences(j["病机"])
            if "牵引治疗" in j:
                j["牵引治疗"] = utils.divide_into_sentences(j["牵引治疗"])
            curr_disease["中药方案"].append(j)

with open("fusion.json", "w") as f:
    json.dump(fusion, f, indent="\t", ensure_ascii=False)
