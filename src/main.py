#!/usr/bin/python3

"""
For test of the transh module.

Composed by Zhand Danyang @THU
Last Revision: Sep 6th, 2019
"""

import sys
sys.path.insert(0, "../lib")

import argparse

import transh

import rdflib
import torch

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str, choices=["predict", "train"], required=True, help="Run prediction or training")
    parser.add_argument("--checkpoint, -k", default="checkpoints/checkpoint-epoch80-loss0.1319.pkl", type=str, required=False, help="Checkpoint to load")

    parser.add_argument("--names", action="append", nargs="+", type=str, required=False, help="Name of medicine components in a recipe, i.e. the \"material\" node in graph")
    parser.add_argument("--ids", action="append", nargs="+", type=int, required=False, help="Id of medicine components in a recipe, i.e. the \"material\" node in graph")

    parser.add_argument("--graph", defaul="../graph/graph", type=str, required=False, help="Graph to load")
    parser.add_argument("--save", defaul="checkpoints", type=str, required=False, help="Path to save checkpoints")
    parser.add_argument("--max-epoch", type=int, required=False, help="Max epoch to train")
    args = parser.parse_args()

    if args.action=="predict":
        pass
        # TODO
    elif args.action=="train":

        if args.graph is None:
            sys.stderr.write("No graph file determined!\n")
            exit(1)
        elif not os.path.exists(args.graph):
            sys.stderr.write("Graph file not found!\n")
            exit(2)

        if args.max_epoch is None:
            sys.stderr.write("Max epoch not determined!\n")
            exit(3)

        graph = rdflib.Graph()
        graph.parse(args.graph)

        if args.checkpoint is None:
            mappings, model, node_stat, dataloader = transh.graph_stat(graph,
                    batch_size=500, embedding_dim=50)
        else:
            state_dict = torch.load(args.checkpoint)
            mappings = state_dict["mappings"]
            model = state_dict["model"]
        checkpoint = transh.train(mappings, model, dataloader, node_stat,
                gamma=2., soft_constraints_weights=0.25,
                max_epoch=args.max_epoch, save_interval=20,
                epsilon=1e-3,
                print_interval=1, print_process=True)

        print(checkpoint)
