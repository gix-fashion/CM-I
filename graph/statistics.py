#!/usr/bin/python3

"""
Composed by Zhand Danyang @THU
"""

import sys
sys.path.insert(0, "../lib")

import utils

import rdflib
import os.path

graph = rdflib.Graph()
graph.parse("graph")

subjects = set(graph.subjects())|set(graph.objects())
subjects = set(str(s) for s in subjects)
recipes = set(int(s.split("#")[-1]) for s in subjects if s.startswith("http://ch-i.gix-fashion.cn/recipe#"))
materials = set(int(s.split("#")[-1]) for s in subjects if s.startswith("http://ch-i.gix-fashion.cn/material#"))
symptoms = set(int(s.split("#")[-1]) for s in subjects if s.startswith("http://ch-i.gix-fashion.cn/symptom#"))
effects = set(int(s.split("#")[-1]) for s in subjects if s.startswith("http://ch-i.gix-fashion.cn/effect#"))
pathogenises = set(int(s.split("#")[-1]) for s in subjects if s.startswith("http://ch-i.gix-fashion.cn/pathogenisis#"))

print("""Number of Triplets: {:d}
Number of Entities: {:d}

Number of Recipes: {:d}
Number of Materials: {:d}
Number of Symptoms: {:d}
Number of Effectes: {:d}
Number of Pathogenises: {:d}

Number of Relations: {:d}""".format(
    len(graph),
    len(subjects),
    len(recipes),
    len(materials),
    len(symptoms),
    len(effects),
    len(pathogenises),
    6))

#effect_keywords
#material_keywords
#pathogenisis_keywords
#recipe_keywords
#symptom_keywords

effect_keywords, _ = utils.load_rdf_keywords_from_trivial_list("std_keywords/effect_keywords")
material_keywords, _ = utils.load_rdf_keywords_from_trivial_list("std_keywords/material_keywords")
pathogenisis_keywords, _ = utils.load_rdf_keywords_from_trivial_list("std_keywords/pathogenisis_keywords")
recipe_keywords, _ = utils.load_rdf_keywords_from_trivial_list("std_keywords/recipe_keywords")
symptom_keywords, _ = utils.load_rdf_keywords_from_trivial_list("std_keywords/symptom_keywords")

effect_keywords = [kw for kw in effect_keywords if kw[0] in effects]
material_keywords = [kw for kw in material_keywords if kw[0] in materials]
pathogenisis_keywords = [kw for kw in pathogenisis_keywords if kw[0] in pathogenises]
recipe_keywords = [kw for kw in recipe_keywords if kw[0] in recipes]
symptom_keywords = [kw for kw in symptom_keywords if kw[0] in symptoms]

with open(os.path.join("present_keywords/", "effect_keywords"), "w") as f:
	for kw in effect_keywords:
		f.write("{:d}\t{:}\n".format(kw[0], "\t".join(kw[1])))
with open(os.path.join("present_keywords/", "material_keywords"), "w") as f:
	for kw in material_keywords:
		f.write("{:d}\t{:}\n".format(kw[0], "\t".join(kw[1])))
with open(os.path.join("present_keywords/", "pathogenisis_keywords"), "w") as f:
	for kw in pathogenisis_keywords:
		f.write("{:d}\t{:}\n".format(kw[0], "\t".join(kw[1])))
with open(os.path.join("present_keywords/", "recipe_keywords"), "w") as f:
	for kw in recipe_keywords:
		f.write("{:d}\t{:}\n".format(kw[0], "\t".join(kw[1])))
with open(os.path.join("present_keywords/", "symptom_keywords"), "w") as f:
	for kw in symptom_keywords:
		f.write("{:d}\t{:}\n".format(kw[0], "\t".join(kw[1])))
