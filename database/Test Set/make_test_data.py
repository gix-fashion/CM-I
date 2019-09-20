#!/usr/bin/python3

import sys
sys.path.insert(0, "../../lib")

import utils
import json

import os
import os.path

extract_keywords = lambda statement, keyword_set:\
        (kw_id for kw_id, kws in keyword_set if any(kw in statement for kw in kws))

material_keywords, material_keyword_mappings = utils.load_rdf_keywords_from_trivial_list("../../graph/present_keywords/material_keywords")
effect_keywords, effect_keyword_mappings = utils.load_rdf_keywords_from_trivial_list("../../graph/present_keywords/effect_keywords")
symptom_keywords, symptom_keyword_mappings = utils.load_rdf_keywords_from_trivial_list("../../graph/present_keywords/symptom_keywords")

raw_datas = os.listdir("../中成药/data")
raw_datas = (f for f in raw_datas if f.endswith(".json"))
dataset = []
# items in dataset:
# {
#   "Medicine": <str>,
#   "Materials": <list of ints>,
#   "Effects": <list of ints>,
#   "Symptoms": <list of ints>
# }
for rd in raw_datas:
    with open(os.path.join("../中成药/data", rd), encoding='gb18030') as f:
        raw_item = json.load(f)
    item = {
            "Medicine": "",
            "Materials": [],
            "Effects": [],
            "Symptoms": []
    }
    if "药名" in raw_item:
        item["Medicine"] = raw_item["药名"]
    if "药方组成" in raw_item:
        item["Materials"] += extract_keywords(raw_item["药方组成"], material_keywords)
    if "处方" in raw_item:
        item["Materials"] += extract_keywords(raw_item["处方"], material_keywords)
    if "功能主治" in raw_item:
        item["Effects"] += extract_keywords(raw_item["功能主治"], effect_keywords)
        item["Symptoms"] += extract_keywords(raw_item["功能主治"], symptom_keywords)
    if "功效与主治" in raw_item:
        item["Effects"] += extract_keywords(raw_item["功效与主治"], effect_keywords)
        item["Symptoms"] += extract_keywords(raw_item["功效与主治"], symptom_keywords)
    if "临床应用" in raw_item:
        item["Symptoms"] += extract_keywords(raw_item["临床应用"], symptom_keywords)
    dataset.append(item)

with open("test_set.json", "w") as f:
    json.dump(dataset, f, indent="\t", ensure_ascii=False)
