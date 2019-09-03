#!/usr/bin/python3

"""
Constructs the subgraph on the "药材" (material) side.

Composed by Zhand Danyang @THU
Last Revision: Sep 3rd, 2019
"""

import sys
sys.path.insert(0, "../lib")
sys.path.append("../药材三元组/")

import rdflib
import rdf_medicine_namespace

import rdf_namespace

import utils

material_keywords, material_keyword_mappings = utils.load_rdf_keywords_from_trivial_list("../药材三元组/Medicines")
effect_keywords, effect_keyword_mappings = utils.load_rdf_keywords_from_trivial_list("../database/药材/功效关键词")
symptom_keywords, symptom_keyword_mappings = utils.load_rdf_keywords_from_trivial_list("../database/药材/病症_关键词")

old_graph = rdflib.Graph()
old_graph.parse("../药材三元组/subgraph_medicine")

new_graph = rdflib.Graph()

# material -> effect
for mat, eft in old_graph.subject_objects(predicate=rdf_medicine_namespace.has_effect):
    eft_ids = (kw_id for kw_id, kws in effect_keywords if any(kw in str(eft).split("#")[-1] for kw in kws))
    for eid in eft_ids:
        new_graph.add((rdf_namespace.material[str(material_keyword_mappings[str(mat).split("#")[-1]])],
            rdf_namespace.has_effect,
            rdf_namespace.effect[str(eid)]))

# material -> symptom
for mat, spt in old_graph.subject_objects(predicate=rdf_medicine_namespace.major_in):
    spt_ids = (kw_id for kw_id, kws in symptom_keywords if any(kw in str(spt).split("#")[-1] for kw in kws))
    for sid in spt_ids:
        new_graph.add((rdf_namespace.material[str(material_keyword_mappings[str(mat).split("#")[-1]])],
            rdf_namespace.major_in,
            rdf_namespace.symptom[str(sid)]))

new_graph.serialize(destination="subgraph_wrt_medicine", format="xml")
