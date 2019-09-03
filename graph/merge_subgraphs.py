#!/usr/bin/python3

"""
Merge two subgraphs.

Composed by Zhand Danyang @THU
Last Revision: Sep 3rd, 2019
"""

import sys
sys.path.insert(0, "../lib")

import utils
import itertools

import json
import zipfile
import os
import os.path

import rdf_namespace
import rdflib

recipe_subgraph = rdflib.Graph()
recipe_subgraph.parse("subgraph_wrt_recipe")
material_subgraph = rdflib.Graph()
material_subgraph.parse("subgraph_wrt_medicine")
graph = rdflib.Graph()
graph = recipe_subgraph|material_subgraph

with open("../database/方剂/常用中药方剂.json") as f:
    database = json.load(f)
    database = itertools.chain.from_iterable(db.values() for db in database.values())
    database = itertools.chain.from_iterable(database)
    common_chinese_drug_recipes = list(database)
    # list of dict {方剂名, 组成, 功用(effect+sysmtom)}
with open("../database/方剂/中药配方大全.json") as f:
    database = json.load(f)
    database = itertools.chain.from_iterable(v for k, v in database.items() if k not in ["药物药性疗效表", "祖传秘方"])
    chinese_drug_recipe_encyclopaedia = list(database)
    # list of {方剂名, 组方, 适应症, 方解, 药物功效}
with open("../database/方剂/中药配方.json") as f:
    database = json.load(f)
    database = itertools.chain.from_iterable(database.values())
    chinese_drug_recipes = list(database)
    # list of {方剂名, 组方}

material_keywords, material_keyword_mappings = utils.load_rdf_keywords_from_trivial_list("../药材三元组/Medicines")
recipe_keywords, recipe_keyword_mappings = utils.load_rdf_keywords_from_trivial_list("../database/方剂/方剂关键词")
symptom_keywords, symptom_keyword_mappings = utils.load_rdf_keywords_from_trivial_list("../database/药材/病症_关键词")

# process data.zip about recipes
# involving relations: recipe -> materail & recipe -> symptom
#with zipfile.ZipFile("../database/方剂#24855/data.zip") as zf:
#namelist = zf.namelist()
namelist = os.listdir("../database/方剂#24855/data")
for n in namelist:
    #with zf.open(n) as f:
    with open(os.path.join("../database/方剂#24855/data", n), encoding='gb18030') as f:
        database = json.load(f)
        #database = json.loads(lines)
    rcp_ids = [kw_id for kw_id, kws in recipe_keywords if any(kw in n for kw in kws)]
    if "【处方】" in database:
        mat_ids = (kw_id for kw_id, kws in material_keywords if any(kw in database["【处方】"] for kw in kws))
        for rcp, mat in itertools.product(rcp_ids, mat_ids):
            graph.add((rdf_namespace.recipe[str(rcp)],
                rdf_namespace.comprises,
                rdf_namespace.material[str(mat)]))
    if "【功能主治】" in database:
        spt_ids = (kw_id for kw_id, kws in symptom_keywords if any(kw in database["【功能主治】"] for kw in kws))
        for rcp, spt in itertools.product(rcp_ids, spt_ids):
            graph.add((rdf_namespace.recipe[str(rcp)],
                rdf_namespace.major_in,
                rdf_namespace.symptom[str(spt)]))

# add relations between recipes and materials
for i, entry in enumerate(common_chinese_drug_recipes):
    if "方剂名" not in entry:
        sys.stderr.write("The {:d}-th entry is without key \"方剂名\"!\n".format(i))
        sys.stderr.flush()
        continue
    if "组成" not in entry:
        sys.stderr.write("Entry {:} is without key \"组成\"!\n".format(entry["方剂名"]))
        sys.stderr.flush()
        continue
    recipe_ids = (kw_id for kw_id, kws in recipe_keywords if any(kw in entry["方剂名"] for kw in kws))
    for recipe_id, material_group in itertools.product(recipe_ids, material_keywords):
        if any(kw in entry["组成"] for kw in material_group[1]):
            graph.add((rdf_namespace.recipe[str(recipe_id)],
                rdf_namespace.major_in,
                rdf_namespace.symptom[str(material_group[0])]))

for i, entry in enumerate(chinese_drug_recipe_encyclopaedia):
    if "方剂名" not in entry:
        sys.stderr.write("The {:d}-th entry is without key \"方剂名\"!\n".format(i))
        sys.stderr.flush()
        continue
    if "组方" not in entry:
        sys.stderr.write("Entry {:} is without key \"组方\"!\n".format(entry["方剂名"]))
        sys.stderr.flush()
        continue
    recipe_ids = (kw_id for kw_id, kws in recipe_keywords if any(kw in entry["方剂名"] for kw in kws))
    for recipe_id, material_group in itertools.product(recipe_ids, material_keywords):
        if any(kw in entry["组方"] for kw in material_group[1]):
            graph.add((rdf_namespace.recipe[str(recipe_id)],
                rdf_namespace.major_in,
                rdf_namespace.symptom[str(material_group[0])]))

for i, entry in enumerate(chinese_drug_recipes):
    if "方剂名" not in entry:
        sys.stderr.write("The {:d}-th entry is without key \"方剂名\"!\n".format(i))
        sys.stderr.flush()
        continue
    if "组方" not in entry:
        sys.stderr.write("Entry {:} is without key \"组方\"!\n".format(entry["方剂名"]))
        sys.stderr.flush()
        continue
    recipe_ids = (kw_id for kw_id, kws in recipe_keywords if any(kw in entry["方剂名"] for kw in kws))
    for recipe_id, material_group in itertools.product(recipe_ids, material_keywords):
        if any(kw in entry["组方"] for kw in material_group[1]):
            graph.add((rdf_namespace.recipe[str(recipe_id)],
                rdf_namespace.major_in,
                rdf_namespace.symptom[str(material_group[0])]))

# add information about disease categories
# Nope, I don't want to work with these

graph.serialize(destination="graph", format="xml")
