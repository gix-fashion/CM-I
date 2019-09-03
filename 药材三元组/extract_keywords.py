#!/usr/bin/python3

import rdflib
import rdf_medicine_namespace

graph = rdflib.Graph()
graph.parse("subgraph_medicine")

medicines = set(graph.subjects())
medicines = (str(m) for m in medicines)
medicines = (m.split("#")[-1] for m in medicines)

with open("Medicines", "w") as f:
    for m in medicines:
        f.write(m + "\n")

effects = set(graph.objects(predicate=rdf_medicine_namespace.has_effect))
effects = (str(e) for e in effects)
effects = (e.split("#")[-1] for e in effects)
with open("Effectes", "w") as f:
    for e in effects:
        f.write(e + "\n")
