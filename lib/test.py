#!/usr/bin/python3

import transh

import rdflib

graph = rdflib.Graph()
graph.parse("database/subgraph_wrt_recipe")

model, node_stat, dataloader = transh.graph_stat(graph)
checkpoint = transh.train(model, dataloader, node_stat, print_process=True)
