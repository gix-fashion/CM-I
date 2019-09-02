#!/usr/bin/python3

"""
For test of the transh module.

Composed by Zhand Danyang @THU
"""

import transh

import rdflib

graph = rdflib.Graph()
graph.parse("database/subgraph_wrt_recipe")

model, node_stat, dataloader = transh.graph_stat(graph)
checkpoint = transh.train(model, dataloader, node_stat, print_process=True)
