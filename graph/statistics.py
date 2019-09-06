#!/usr/bin/python3

"""
Composed by Zhand Danyang @THU
"""

import rdflib

graph = rdflib.Graph()
graph.parse("graph")

subjects = set(graph.subjects())|set(graph.objects())
subjects = [str(s) for s in subjects]
recipes = [s for s in subjects if s.startswith("http://ch-i.gix-fashion.cn/recipe#")]
materials = [s for s in subjects if s.startswith("http://ch-i.gix-fashion.cn/material#")]
symptoms = [s for s in subjects if s.startswith("http://ch-i.gix-fashion.cn/symptom#")]
effects = [s for s in subjects if s.startswith("http://ch-i.gix-fashion.cn/effect#")]
pathogenises = [s for s in subjects if s.startswith("http://ch-i.gix-fashion.cn/pathogenisis#")]

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
