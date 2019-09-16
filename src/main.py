#!/usr/bin/python3

"""
For test of the transh module.

Composed by Zhand Danyang @THU
Last Revision: Sep 6th, 2019
"""

import sys
sys.path.insert(0, "../lib")
sys.path.append("../graph")

import argparse

import transh

import rdflib
import torch
import rdf_namespace
import utils

_project = lambda n, r: n - torch.sum(r*n, axis=-1, keepdim=True)*n
_distance_to_probability = lambda x: (2.-x)/(x+2.)
def _find_topk(ns, projs, r, topk):
    center = torch.mean(projs, axis=0)
    error = torch.sqrt(torch.sum(
        (_project(ns, r[0])-center)**2, axis=-1))
    indices = torch.argsort(error, descending=True)[:topk]
    topks = ns[indices]
    return indices, topks, error[indices]

def _predict(medicine_rdfs, recipe_rdfs, effect_rdfs, symptom_rdfs, state_dict, topk=5):
    node_mappings = state_dict["mappings"][0]
    relation_mappings = state_dict["mappings"[1]]
    node_embeddings = state_dict["model"][0]
    relation_embeddings = state_dict["model"][1]

    medicines_id = [node_mappings[mrdf] for mrdf in medicine_rdfs]
    medicines_embedding = node_embeddings[medicines_id]
    recipes_id = [node_mappings[rrdf] for rrdf in recipe_rdfs]
    recipes_embedding = node_embeddings[recipes_id]
    effects_id = [node_mappings[erdf] for erdf in effect_rdfs]
    effects_embedding = node_embeddings[effects_id]
    symptoms_id = [node_mappings[srdf] for srdf in symptom_rdfs]
    symptoms_embedding = node_embeddings[symptoms_id]

    comprises = relation_embeddings[relation_mappings[rdf_namespace.comprises]]
    recipe_comprises_projections = _project(medicines_embedding, comprises[0]) - comprises[1]
    _, preserved_recipes, _ = _find_topk(recipes_embedding, recipe_comprises_projections, comprises, topk)

    major_in = relation_embeddings[relation_mappings[rdf_namespace.major_in]]
    effect_major_in_projections = _project(preserved_recipes, major_in[0]) + major_in[1]
    preserved_effects, _, effect_errors = _find_topk(effects_embedding, effect_major_in_projections, major_in, topk)

    has_effect = relation_embeddings[relation_mappings[rdf_namespace.has_effect]]
    symptom_has_effect_projections = _project(preserved_recipes, has_effect[0]) + has_effect[1]
    preserved_symptoms, _, symptom_errors = _find_topk(symptoms_embedding, symptom_has_effect_projections, has_effect, topk)

    return preserved_effects, preserved_symptoms, effect_errors, symptom_errors

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str, choices=["predict", "train"], required=True, help="Run prediction or training")
    parser.add_argument("--checkpoint, -k", default="../checkpoints/checkpoint-epoch1400-loss0.0879.pkl", type=str, required=False, help="Checkpoint to load")
    # keys in state_dict: epoch, mappings, model, loss

    parser.add_argument("--names", action="append", nargs="+", type=str, required=False, help="Name of medicine components in a recipe, i.e. the \"material\" node in graph")
    parser.add_argument("--ids", action="append", nargs="+", type=int, required=False, help="Id of medicine components in a recipe, i.e. the \"material\" node in graph")
    parser.add_argument("--name-id-mappings-dir", defaul="../graph/present_keywords", type=str, required=False, help="Directory of mappings")
    parser.add_argument("--topk", defaul=5, type=int, required=False, help="topk")

    parser.add_argument("--graph", defaul="../graph/graph", type=str, required=False, help="Graph to load")
    parser.add_argument("--save", defaul="checkpoints", type=str, required=False, help="Path to save checkpoints")
    parser.add_argument("--save-interval", defaul=100, type=int, required=False, help="Interval of saving checkpoints")
    parser.add_argument("--max-epoch", defaul=2000, type=int, required=False, help="Max epoch to train")
    args = parser.parse_args()

    if args.action=="predict":

        if args.checkpoint is None:
            sys.stderr.write("No checkpoint determined!\n")
            exit(1)
        elif not os.path.exists(args.checkpoint):
            sys.stderr.write("Checkpoint not found!\n")
            exit(2)

        if not os.path.isdir(args.name_id_mappings_dir):
            sys.stderr.write("`{:}` is not a directory.".format(args.name_id_mappings_dir))
            exit(2)
        node_categories = ["effect", "material", "pathogenisis", "recipe", "symptom"]
        node_keyword_mappings = {}
        for nc in node_categories:
            try:
                node_keyword_mappings[nc] = utils.load_rdf_keywords_from_trivial_list(
                        os.path.join(args.name_id_mappings_dir, nc + "_keywords"))
            except:
                sys.stderr.write("Failed to load keyword file {:}".format(
                    os.path.join(args.name_id_mappings_dir, nc + "_keywords")))
                exit(3)

        if args.names is not None:
            medicines = [rdf_namespace.material[str(node_categories["material"][1][mn])]
                    for mn in args.names if mn in node_categories["material"][1]]
        elif args.ids is not None:
            medicine_ids = [mid for mid, _ in node_categories["material"][0]]
            medicines = [rdf_namespace.material[str(mid)] for mid in args.ids if mid in medicine_ids]
        else:
            exit(0)

        try:
            state_dict = torch.load(args.checkpoint)
        except:
            sys.stderr.write("Failed to load checkpoint!\n")
            exit(3)

        recipes = [rdf_namespace.recipe[str(rid)] for rid, _ in node_categories["recipe"][0]]
        effects = [rdf_namespace.effect[str(eid)] for eid, _ in node_categories["effect"][0]]
        symptoms = [rdf_namespace.symptom[str(sid)] for sid, _ in node_categories["symptom"][0]]

        effects, symptoms, effect_errors, symptom_errors = _predict(medicines, recipes, effects, symptoms, state_dict, args.topk)
        effect_probabilities = _distance_to_probability(effect_errors)
        symptom_probabilities = _distance_to_probability(symptom_errors)

        inverse_mappings = dict((i, s) for s, i in state_dict["mappings"].items())

        effects = effects.cpu().numpy()
        effects = (inverse_mappings[i] for i in effects)
        effects = (str(e).split("#")[-1] for e in effects)
        effect_mappings = dict(node_categories["effect"][0])
        effects = (effect_mappings[int(e)][0] for e in effects)

        symptoms = effects.cpu().numpy()
        symptoms = (inverse_mappings[i] for i in symptoms)
        symptoms = (str(s).split("#")[-1] for s in symptoms)
        symptom_mappings = dict(node_categories["symptom"][0])
        symptoms = (symptom_mappings[int(s)][0] for s in symptoms)

        print("预测功效：")
        for e, p in zip(effects, effect_probabilities):
            print("{:}: {:.2f}%".format(e, 100.*p))
        print()
        print("预测适应症：")
        for s, p in zip(symptoms, symptom_probabilities):
            print("{:}: {:.2f}%".format(s, 100.*p))

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
            try:
                state_dict = torch.load(args.checkpoint)
            except:
                sys.stderr.write("Failed to load checkpoint!\n")
                exit(3)
            mappings = state_dict["mappings"]
            model = state_dict["model"]
        checkpoint = transh.train(mappings, model, dataloader, node_stat,
                gamma=2., soft_constraints_weights=0.25,
                max_epoch=args.max_epoch, save_interval=args.save_interval, save_dir=args.save,
                epsilon=1e-3,
                print_interval=50, print_process=True)

        print(checkpoint)
