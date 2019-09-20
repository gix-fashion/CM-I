#!/usr/bin/python3

"""
For test of the transh module.

Last Revision: Sep 20th, 2019
"""

import sys
sys.path.insert(0, "../lib")
sys.path.append("../graph")

import argparse
import terminaltables

import transh
import numpy as np

import rdflib
import torch
import rdf_namespace
import utils
import json
import os
import os.path

_project = lambda n, r: n - torch.sum(r*n, dim=-1, keepdim=True)*n
_distance_to_probability = lambda x: (2.-x)/(x+2.)
_probability_to_distance = lambda p: 2.*(1.-p)/(p+1.)
def _find_topk(ns, projs, r, error_thrd, topk):
    center = torch.mean(projs, dim=0)
    error = torch.sqrt(torch.sum(
        (_project(ns, r[0])-center)**2, dim=-1))
    sorted_indices = torch.argsort(error)
    nb_matched = torch.sum(error<=error_thrd).tolist()
    indices = sorted_indices[:max(nb_matched, topk)]
    topks = ns[indices]
    return indices, topks, error[indices]

def _predict(medicine_rdfs, recipe_rdfs, effect_rdfs, symptom_rdfs, state_dict, error_thrd=.5, topk = 5):
    node_mappings = state_dict["mappings"][0]
    relation_mappings = state_dict["mappings"][1]
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
    _, preserved_recipes, _ = _find_topk(recipes_embedding, recipe_comprises_projections, comprises, error_thrd, topk = 5)

    has_effect = relation_embeddings[relation_mappings[rdf_namespace.has_effect]]
    effect_has_effect_projections = _project(preserved_recipes, has_effect[0]) + has_effect[1]
    preserved_effects, _, effect_errors = _find_topk(effects_embedding, effect_has_effect_projections, has_effect, error_thrd, topk = 5)

    major_in = relation_embeddings[relation_mappings[rdf_namespace.major_in]]
    sysmtom_major_in_projections = _project(preserved_recipes, major_in[0]) + major_in[1]
    preserved_symptoms, _, symptom_errors = _find_topk(symptoms_embedding, sysmtom_major_in_projections, major_in, error_thrd, topk = 5)

    return preserved_effects, preserved_symptoms, effect_errors, symptom_errors

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str, choices=["predict", "train", "test"], help="Run prediction or training")
    parser.add_argument("--checkpoint", "-k", default="../checkpoints/checkpoint-epoch800-loss0.0784.pkl", type=str, required=False, help="Checkpoint to load")
    # keys in state_dict: epoch, mappings, model, loss

    parser.add_argument("--names", action="append", nargs="+", type=str, required=False, help="Name of medicine components in a recipe, i.e. the \"material\" node in graph")
    parser.add_argument("--ids", action="append", nargs="+", type=int, required=False, help="Id of medicine components in a recipe, i.e. the \"material\" node in graph")
    parser.add_argument("--name-id-mappings-dir", default="../graph/present_keywords", type=str, required=False, help="Directory of mappings")
    parser.add_argument("--topk", default=5, type=int, required=False, help="topk")
    parser.add_argument("--probability", default=.5, type=float, required=False, help="probability threshold")

    parser.add_argument("--graph", default="../graph/graph", type=str, required=False, help="Graph to load")
    parser.add_argument("--save", default="checkpoints", type=str, required=False, help="Path to save checkpoints")
    parser.add_argument("--save-interval", default=100, type=int, required=False, help="Interval of saving checkpoints")
    parser.add_argument("--max-epoch", default=1000, type=int, required=False, help="Max epoch to train")

    parser.add_argument("--test-set", default="../database/Test Set/test_set.json", type=str, required=False, help="Path to test set")
    args = parser.parse_args()

    if args.action=="predict":

        if args.checkpoint is None:
            sys.stderr.write("No checkpoint determined!\n")
            exit(1)
        elif not os.path.exists(args.checkpoint):
            sys.stderr.write("Checkpoint not found!\n")
            exit(2)

        if not os.path.isdir(args.name_id_mappings_dir):
            sys.stderr.write("`{:}` is not a directory.\n".format(args.name_id_mappings_dir))
            exit(2)
        node_categories = ["effect", "material", "pathogenisis", "recipe", "symptom"]
        node_keyword_mappings = {}
        for nc in node_categories:
            try:
                node_keyword_mappings[nc] = utils.load_rdf_keywords_from_trivial_list(
                        os.path.join(args.name_id_mappings_dir, nc + "_keywords"))
            except:
                sys.stderr.write("Failed to load keyword file {:}\n".format(
                    os.path.join(args.name_id_mappings_dir, nc + "_keywords")))
                exit(3)

        if args.names is not None:
            medicines = [rdf_namespace.material[str(node_keyword_mappings["material"][1][mn])]
                    for mn in args.names if mn in node_keyword_mappings["material"][1]]
        elif args.ids is not None:
            medicine_ids = [mid for mid, _ in node_keyword_mappings["material"][0]]
            medicines = [rdf_namespace.material[str(mid)] for mid in args.ids if mid in medicine_ids]
        else:
            exit(0)

        try:
            state_dict = torch.load(args.checkpoint)
        except:
            sys.stderr.write("Failed to load checkpoint!\n")
            exit(3)

        recipes = [rdf_namespace.recipe[str(rid)] for rid, _ in node_keyword_mappings["recipe"][0]]
        effects = [rdf_namespace.effect[str(eid)] for eid, _ in node_keyword_mappings["effect"][0]]
        symptoms = [rdf_namespace.symptom[str(sid)] for sid, _ in node_keyword_mappings["symptom"][0]]

        error_thrd = _probability_to_distance(args.probability)

        effects, symptoms, effect_errors, symptom_errors = _predict(medicines, recipes, effects, symptoms, state_dict, error_thrd, args.topk)
        effect_probabilities = _distance_to_probability(effect_errors).cpu().numpy()
        symptom_probabilities = _distance_to_probability(symptom_errors).cpu().numpy()

        inverse_mappings = dict((i, s) for s, i in state_dict["mappings"][0].items())

        effects = effects.cpu().numpy()
        effects = (inverse_mappings[i] for i in effects)
        effects = (str(e).split("#")[-1] for e in effects)
        effect_mappings = dict(node_keyword_mappings["effect"][0])
        effects = (effect_mappings[int(e)][0] for e in effects)

        symptoms = symptoms.cpu().numpy()
        symptoms = (inverse_mappings[i] for i in symptoms)
        symptoms = (str(s).split("#")[-1] for s in symptoms)
        symptom_mappings = dict(node_keyword_mappings["symptom"][0])
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

    elif args.action=="test":

        if args.checkpoint is None:
            sys.stderr.write("No checkpoint determined!\n")
            exit(1)
        elif not os.path.exists(args.checkpoint):
            sys.stderr.write("Checkpoint not found!\n")
            exit(2)

        if not os.path.isdir(args.name_id_mappings_dir):
            sys.stderr.write("`{:}` is not a directory.\n".format(args.name_id_mappings_dir))
            exit(2)
        node_categories = ["effect", "material", "pathogenisis", "recipe", "symptom"]
        node_keyword_mappings = {}
        for nc in node_categories:
            try:
                node_keyword_mappings[nc] = utils.load_rdf_keywords_from_trivial_list(
                        os.path.join(args.name_id_mappings_dir, nc + "_keywords"))
            except:
                sys.stderr.write("Failed to load keyword file {:}\n".format(
                    os.path.join(args.name_id_mappings_dir, nc + "_keywords")))
                exit(3)

        if not os.path.exists(args.test_set):
            sys.stderr.write("Test set not found!\n")
            exit(2)
        try:
            with open(args.test_set) as f:
                test_set = json.load(f)
        except:
            sys.stderr.write("Failed to load the test set!\n")
            exit(3)

        try:
            state_dict = torch.load(args.checkpoint)
        except:
            sys.stderr.write("Failed to load checkpoint!\n")
            exit(3)

        recipe_base = [rdf_namespace.recipe[str(rid)] for rid, _ in node_keyword_mappings["recipe"][0]]
        effect_base = [rdf_namespace.effect[str(eid)] for eid, _ in node_keyword_mappings["effect"][0]]
        symptom_base = [rdf_namespace.symptom[str(sid)] for sid, _ in node_keyword_mappings["symptom"][0]]

        error_thrd = _probability_to_distance(args.probability)
        #print(state_dict.keys())
        inverse_mappings = dict((i, s) for s, i in state_dict["mappings"][0].items())

        nb_sample = len(test_set)
        effect_metrics = np.zeros((3, nb_sample)) # for recalls, IoUs and precisions
        symptom_metrics = np.zeros((3, nb_sample))

        def metrics(groundtruth, prediction):
            """
            return recall, IoU, precision
            """

            prediction = set(prediction)
            if len(prediction)==0:
                return 0., 0., 0.
            groundtruth = set(groundtruth)
            if len(groundtruth)==0:
                return 1., 0., 0.
            intersection = groundtruth&prediction
            union = groundtruth|prediction
            return float(len(intersection))/len(groundtruth),\
                    float(len(intersection))/len(union),\
                    float(len(intersection))/len(prediction)
        def print_metrics(xx_metrics):
            avg_metrics = np.mean(xx_metrics, axis=1)
            print("""Average Recall: {:.4f}
Average IoU: {:.4f}
Average Precision: {:.4f}""".format(
                    avg_metrics[0],
                    avg_metrics[1],
                    avg_metrics[2]))
            print()

            thresholds = np.arange(0.1, 1.0, 0.1)
            thresholds_str = ["{:.1f}".format(thrd) for thrd in thresholds]

            def print_metrics(xx_metrics, threshold_kind):
                accuracies = []
                for thrd in thresholds:
                    accuracies.append(
                            np.sum(xx_metrics>=thrd)/float(nb_sample))
                table = terminaltables.AsciiTable([
                    [threshold_kind] + thresholds_str,
                    ["Accuracy"] + ["{:.4f}".format(acc) for acc in accuracies]
                ], title="Accuracy w.r.t. " + threshold_kind)
                table.inner_row_border = True
                print(table.table)

            # Recall Threshold
            print_metrics(xx_metrics[0], "Recall Threshold")
            print()

            # IoU Threshold
            print_metrics(xx_metrics[1], "IoU Threshold")
            print()

            # Precision Threshold
            print_metrics(xx_metrics[2], "Precision Threshold")
            print()

        for i, sample in enumerate(test_set):
            medicines = [rdf_namespace.material[str(m)] for m in sample["Materials"]]
            effects, symptoms, effect_errors, symptom_errors = _predict(medicines, recipe_base, effect_base, symptom_base, state_dict, error_thrd, args.topk)

            effects = effects.cpu().numpy()
            effects = (inverse_mappings[i] for i in effects)
            effects = (str(e).split("#")[-1] for e in effects)
            effects = [int(e) for e in effects]
            ef_recall, ef_iou, ef_precision = metrics(sample["Effects"], effects)
            effect_metrics[:, i] = [ef_recall, ef_iou, ef_precision]

            symptoms = symptoms.cpu().numpy()
            symptoms = (inverse_mappings[i] for i in symptoms)
            symptoms = (str(s).split("#")[-1] for s in symptoms)
            symptoms = [int(s) for s in symptoms]
            sm_recall, sm_iou, sm_precision = metrics(sample["Symptoms"], symptoms)
            symptom_metrics[:, i] = [sm_recall, sm_iou, sm_precision]

        print("Effect Prediction Metrics")
        print()
        print_metrics(effect_metrics)

        print("symptom Prediction Metrics")
        print()
        print_metrics(symptom_metrics)
