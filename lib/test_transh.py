#!/usr/bin/python3

"""
For test of the transh module.

Composed by Zhand Danyang @THU
"""

import transh

import rdflib

graph = rdflib.Graph()
graph.parse("graph")

#print(len(list(graph)))
#print(len(set(graph.subjects())|set(graph.objects())))

mappings, model, node_stat, dataloader = transh.graph_stat(graph,
        batch_size=500, embedding_dim=50)
checkpoint = transh.train(model, dataloader, node_stat,
        gamma=2., soft_constraints_weights=0.25,
        max_epoch=1000, save_interval=20,
        epsilon=1e-3,
        print_interval=1, print_process=True)

print(checkpoint)
