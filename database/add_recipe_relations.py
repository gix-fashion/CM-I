#!/usr/bin/python3

"""
Constructs the subgraph on the "方剂" (recipe) side.

Composed by Zhand Danyang @THU
Last Revision: Aug 28th, 2019
"""

import sys
sys.path.insert(0, "..")

import rdflib
import json

import rdf_namespace

import utils
import itertools

graph = rdflib.Graph()

with open("方剂/常用中药方剂.json") as f:
    database = json.load(f)
    database = itertools.chain.from_iterable(db.values() for db in database.values())
    database = itertools.chain.from_iterable(database)
    common_chinese_drug_recipes = list(database)
    # list of dict {方剂名, 组成, 功用(effect+sysmtom)}
with open("病症/中医常见病症.json") as f:
    database = json.load(f)["常见病"]
    database = ((set(utils.extract_equivalent_expressions(k)), w["子类"]) for k, w in database.items() if "子类" in w)
    database = itertools.chain.from_iterable(
            ((k, w) for w in sub) for k, sub in database)
    chinese_medicine_common_symptoms = list(database)
    # list of (病症, dict{性质, 对策, 给方})
with open("方剂/中药配方大全.json") as f:
    database = json.load(f)
    database = itertools.chain.from_iterable(v for k, v in database.items() if k not in ["药物药性疗效表", "祖传秘方"])
    chinese_drug_recipe_encyclopaedia = list(database)
    # list of {方剂名, 组方, 适应症, 方解, 药物功效}
with open("病症/中华人民共和国中医药行业标准-中医证候诊断标准16.json") as f:
    database = json.load(f)
    database = itertools.chain.from_iterable(((k, v) for v in l) for k, l in database.items())
    prc_chinese_medicine_and_drug_trade_standard_chinese_medicine_symptom_diagnosis_standard_2016 =\
            list(database)
    # list of (疾病科目, dict{病症, 病机, 诊断依据, 症候分类, 疗效评定})

recipe_keywords, recipe_keyword_mappings = utils.load_rdf_keywords_from_trivial_list("方剂/方剂关键词")
effect_keywords, effect_keyword_mappings = utils.load_rdf_keywords_from_trivial_list("药材/功效关键词")
symptom_keywords, symptom_keyword_mappings = utils.load_rdf_keywords_from_trivial_list("药材/病症_关键词")
pathogenisis_keywords, pathogenisis_keyword_mappings = utils.load_rdf_keywords_from_trivial_list("病症/疾病原理性质关键词")

symptom_keyword_set = set(symptom_keyword_mappings)

# recipe -> effect
for i, entry in enumerate(common_chinese_drug_recipes):
    if "方剂名" not in entry:
        sys.stderr.write("The {:d}-th entry is without key \"方剂名\"!\n".format(i))
        sys.stderr.flush()
        continue
    if "功用" not in entry:
        sys.stderr.write("Entry {:} is without key \"功用\"!\n".format(entry["方剂名"]))
        sys.stderr.flush()
        continue
    #if entry["方剂名"] not in recipe_keyword_mappings:
        #sys.stderr.write("\"方剂名\" of entry {:} is not found in keyword file!\n".format(entry["方剂名"]))
        #sys.stderr.flush()
        #continue
    #recipe_id = recipe_keyword_mappings[entry["方剂名"]]
    recipe_ids = (kw_id for kw_id, kws in recipe_keywords if any(kw in entry["方剂名"] for kw in kws))
    for recipe_id, effect_group in itertools.product(recipe_ids, effect_keywords):
        if any(kw in entry["功用"] for kw in effect_group[1]):
            graph.add((rdf_namespace.recipe[str(recipe_id)],
                rdf_namespace.has_effect,
                rdf_namespace.effect[str(effect_group[0])]))

# symptom -> effect
for i, entry in enumerate(chinese_medicine_common_symptoms):
    if len(entry[0])==0:
        sys.stderr.write("The {:d}-th entry is without a legal key!\n".format(i))
        sys.stderr.flush()
        continue
    if "对策" not in entry[1]:
        sys.stderr.write("Entry {:} is without key \"对策\"!\n".format(entry[0]))
        sys.stderr.flush()
        continue
    std_keywords = set(entry[0])&symptom_keyword_set
    if len(std_keywords)>0:
        effect_group = (kw_id for kw_id, kws in effect_keywords if any(kw in entry[1]["对策"] for kw in kws))
        for spt, eft in itertools.product(std_keywords, effect_group):
            graph.add((rdf_namespace.symptom[str(symptom_keyword_mappings[spt])],
                rdf_namespace.treatment_plan,
                rdf_namespace.effect[str(eft)]))

# recipe -> symptom
for i, entry in enumerate(common_chinese_drug_recipes):
    if "方剂名" not in entry:
        sys.stderr.write("The {:d}-th entry is without key \"方剂名\"!\n".format(i))
        sys.stderr.flush()
        continue
    if "功用" not in entry:
        sys.stderr.write("Entry {:} is without key \"功用\"!\n".format(entry["方剂名"]))
        sys.stderr.flush()
        continue
    #if entry["方剂名"] not in recipe_keyword_mappings:
        #sys.stderr.write("\"方剂名\" of entry {:} is not found in keyword file!\n".format(entry["方剂名"]))
        #sys.stderr.flush()
        #continue
    #recipe_id = recipe_keyword_mappings[entry["方剂名"]]
    recipe_ids = (kw_id for kw_id, kws in recipe_keywords if any(kw in entry["方剂名"] for kw in kws))
    for recipe_id, symptom_group in itertools.product(recipe_ids, effect_keywords):
        if any(kw in entry["功用"] for kw in symptom_group[1]):
            graph.add((rdf_namespace.recipe[str(recipe_id)],
                rdf_namespace.applys_on,
                rdf_namespace.symptom[str(symptom_group[0])]))

for i, entry in enumerate(chinese_medicine_common_symptoms):
    if len(entry[0])==0:
        sys.stderr.write("The {:d}-th entry is without a legal key!\n".format(i))
        sys.stderr.flush()
        continue
    if "给方" not in entry[1]:
        sys.stderr.write("Entry {:} is without key \"给方\"!\n".format(entry[0]))
        sys.stderr.flush()
        continue
    std_keywords = set(entry[0])&symptom_keyword_set
    if len(std_keywords)>0:
        recipe_plan = utils.format_recipe_from_str_to_list(entry[1]["给方"])
        recipe_plan = (recipe_keyword_mappings[r] for r in recipe_plan if r in recipe_keyword_mappings)
        for spt, rcp in itertools.product(std_keywords, recipe_plan):
            graph.add((rdf_namespace.recipe[str(rcp)],
                rdf_namespace.applys_on,
                rdf_namespace.symptom[str(symptom_keyword_mappings[spt])]))

for i, entry in enumerate(chinese_drug_recipe_encyclopaedia):
    if "方剂名" not in entry:
        sys.stderr.write("The {:d}-th entry is without key \"方剂名\"!\n".format(i))
        sys.stderr.flush()
        continue
    if "适应症" not in entry:
        sys.stderr.write("Entry {:} is without key \"适应症\"!\n".format(entry["方剂名"]))
        sys.stderr.flush()
        continue
    #if entry["方剂名"] not in recipe_keyword_mappings:
        #sys.stderr.write("\"方剂名\" of entry {:} is not found in keyword file!\n".format(entry["方剂名"]))
        #sys.stderr.flush()
        #continue
    #recipe_id = recipe_keyword_mappings[entry["方剂名"]]
    recipe_ids = (kw_id for kw_id, kws in recipe_keywords if any(kw in entry["方剂名"] for kw in kws))
    for recipe_id, symptom_group in itertools.product(recipe_ids, effect_keywords):
        if any(kw in entry["适应症"] for kw in symptom_group[1]):
            graph.add((rdf_namespace.recipe[str(recipe_id)],
                rdf_namespace.applys_on,
                rdf_namespace.symptom[str(symptom_group[0])]))

# symtopm -> pathogenisis
for _, entry in prc_chinese_medicine_and_drug_trade_standard_chinese_medicine_symptom_diagnosis_standard_2016:
    if "症候分类" not in entry:
        sys.stderr.write("Entry {:} is without key \"症候分类\"!\n".format(entry["病症"]))
        sys.stderr.flush()
        continue
    std_symtom_keywords = (kw_id for kw_id, kws in symptom_keywords if any(kw in entry["病症"] for kw in kws))
    std_pathogenisis_keywords = (kw_id for kw_id, kws in pathogenisis_keywords if any(kw in entry["症候分类"] for kw in kws))
    for spt, phg in itertools.product(std_symtom_keywords, std_pathogenisis_keywords):
        graph.add((rdf_namespace.symptom[str(spt)],
            rdf_namespace.originates_from,
            rdf_namespace.pathogenisis[str(phg)]))

for i, entry in enumerate(chinese_medicine_common_symptoms):
    if len(entry[0])==0:
        sys.stderr.write("The {:d}-th entry is without a legal key!\n".format(i))
        sys.stderr.flush()
        continue
    if "性质" not in entry[1]:
        sys.stderr.write("Entry {:} is without key \"性质\"!\n".format(entry[0]))
        sys.stderr.flush()
        continue
    std_keywords = set(entry[0])&symptom_keyword_set
    if len(std_keywords)>0:
        pathogenisis_group = (kw_id for kw_id, kws in pathogenisis_keywords if any(kw in entry[1]["性质"] for kw in kws))
        for spt, phg in itertools.product(std_keywords, pathogenisis_group):
            graph.add((rdf_namespace.symptom[str(symptom_keyword_mappings[spt])],
                rdf_namespace.originates_from,
                rdf_namespace.effect[str(phg)]))

# effect -> pathogenesis
for i, entry in enumerate(chinese_medicine_common_symptoms):
    key = entry[0] if len(entry[0])>0 else i
    if "性质" not in entry[1]:
        sys.stderr.write("Entry {:} is without key \"性质\"!\n".format(key))
        sys.stderr.flush()
        continue
    if "对策" not in entry[1]:
        sys.stderr.write("Entry {:} is without key \"对策\"!\n".format(key))
        sys.stderr.flush()
        continue
    std_effect_keywords = (kw_id for kw_id, kws in effect_keywords if any(kw in entry[1]["对策"] for kw in kws))
    std_pathogenisis_keywords = (kw_id for kw_id, kws in pathogenisis_keywords if any(kw in entry[1]["性质"] for kw in kws))
    for eft, phg in itertools.product(std_effect_keywords, std_pathogenisis_keywords):
        graph.add((rdf_namespace.symptom[str(eft)],
            rdf_namespace.applys_on,
            rdf_namespace.effect[str(phg)]))

#graph.serialize(destination="subgraph_wrt_recipe", format="nt")
graph.serialize(destination="subgraph_wrt_recipe", format="xml")
