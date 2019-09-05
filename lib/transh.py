# transh.py

"""
A simple implementation of [TransH] method.

[TransH]: Zhen Wang, Jianwen Zhang et al. *Knowledge Graph Embedding by Translating on Hyperplanes*. AAAI 2014

Composed by Zhand Danyang @THU
Last Revision: Sep 2nd
"""

import os
import os.path

import torch
import torch.nn.functional as functional
import torch.optim as optim

import random
import itertools
import numpy as np
import numpy.matlib as matlib

random.seed()

def train(model, dataloader, node_stat,
        max_epoch=500, save_interval=100, save_dir="checkpoints",
        gpus=False, gamma=1., soft_constraints_weights=0.25, epsilon=1e-3,
        print_process=False, print_interval=100):
    """
    Trains a TransH model and returns the model.

    model - a tuple like (E, R), where
        E is array with shape (nb_node, embedding_dim)
        R is array with shape (nb_node, 2, embedding_dim), denoting (w_r, d_r) for each relation type
        all the vectors are expected to be with type of numpy or torch tensor
    dataloader - an iterable, yielding batchs of triplets
    node_stat - dict like {r: d} where
        r is relation id;
        d is a dict with node id as key and a tuple like (tph, hpt) as value;
        for the meaning of tph and hpt, please refer to the paper [TransH]

    max_epoch - the maximum training epoch
    save_interval - the interval of epochs to save a checkpoint
    save_dir - str or path-like object, the target archive path of model checkpoints

    gpus - boolean indicating whether a gpu should be used
    gamma - a margin or bias used in the loss, for details please refer to the paper [TransE] or [TransH]
    soft_constraints_weights - the weights of the soft constraints, for details please refer to the hyper-parameter C in the paper [TransH]
    epsilon - a small threshold to hold the othorgonality between w_r and d_r, for details please refer to the paper [TransH]

    print_process - print the process if is set to True

    return - the path to the checkpoint of the final epoch

    [TransE]: Antoine Bords, Nicolas Usunier et al. *Translating Embeddings for Modeling Multi-relational Data*, 2013
    [TransH]: Zhen Wang, Jianwen Zhang et al. *Knowledge Graph Embedding by Translating on Hyperplanes*. AAAI 2014
    """

    node_embedding = model[0]
    relation_embedding = model[1]
    epsilon **= 2

    if gpus:
        loss = torch.tensor(0., dtype=torch.double).cuda()
        node_embedding = torch.as_tensor(node_embedding).requires_grad_().cuda()
        relation_embedding = torch.as_tensor(relation_embedding).requires_grad_().cuda()
    else:
        loss = torch.tensor(0., dtype=torch.double).cpu()
        node_embedding = torch.as_tensor(node_embedding).requires_grad_().cpu()
        relation_embedding = torch.as_tensor(relation_embedding).requires_grad_().cpu()

    if not os.path.exists(save_dir):
        os.makedirs(save_dir, mode=0o755)

    def fr(h, t, w, d):
        #print(h.shape)
        w = w/torch.sqrt(torch.sum(w**2))
        h_proj = h - torch.matmul(w, h)*w
        #print(h_proj.shape)
        t_proj = t - torch.matmul(w, t)*w
        return torch.sum((h_proj - t_proj + d)**2)
    optm = optim.Adam([node_embedding, relation_embedding], lr=0.005)

    # training process
    is_first_epoch = True
    for epoch, batch in enumerate(dataloader):
        #print("{:d}, {:}".format(epoch, type(batch)))
        if epoch>=max_epoch:
            break

        batch_size = float(len(batch))
        optm.zero_grad()
        loss.fill_(0.)
        for head, relation, tail in batch:
            denominator = float(node_stat[relation][head][0]+node_stat[relation][tail][1])
            replace_head = random.random()<node_stat[relation][head][0]/denominator
            replace_tail = random.random()<node_stat[relation][tail][1]/denominator

            if replace_head:
                while True:
                    new_head = random.randrange(len(node_embedding))
                    if new_head!=head:
                        break
            else:
                new_head = head
            if replace_tail:
                while True:
                    new_tail = random.randrange(len(node_embedding))
                    if new_tail!=tail:
                        break
            else:
                new_tail = tail

            loss += functional.relu(fr(node_embedding[head], node_embedding[tail],
                    relation_embedding[relation][0], relation_embedding[relation][1])-
                            fr(node_embedding[new_head], node_embedding[new_tail],
                                relation_embedding[relation][0], relation_embedding[relation][1])+
                            gamma).double()
        #print(epoch)

        loss += torch.sum(functional.relu(torch.sum(node_embedding**2, axis=1)-1.))
        othorgonality = torch.sum(relation_embedding[:, 0, :]*relation_embedding[:, 1, :], axis=1)**2/\
                torch.sum(relation_embedding[:, 1, :]**2, axis=1)
        loss += torch.sum(functional.relu(othorgonality-epsilon))
        loss /= batch_size

        #print(epoch)

        #if is_first_epoch:
            #loss.backward(retain_graph=True)
        #else:
            #loss.backward()
        loss.backward(retain_graph=True)
        #print(epoch)
        optm.step()
        #print(epoch)

        if epoch%save_interval==0:
            final_checkpoint_name = os.path.join(save_dir, "checkpoint-epoch{:d}-loss{:.4f}.pkl".format(epoch, loss.tolist()))
            torch.save({
                "epoch": epoch,
                "model": (node_embedding, relation_embedding),
                "loss": loss.tolist()
            }, final_checkpoint_name)

        if print_process and epoch % print_interval==0:
            print("Epoch {:d}: Loss - {:.4f}".format(epoch, loss.tolist()))

        is_first_epoch = False

    final_checkpoint_name = os.path.join(save_dir, "checkpoint-epoch{:d}-loss{:.4f}.pkl".format(epoch, loss.tolist()))
    torch.save({
        "epoch": epoch,
        "model": (node_embedding, relation_embedding),
        "loss": loss.tolist()
    }, final_checkpoint_name)

    if print_process:
        print("\nTraining ends.\nEpoch {:d}: Loss - {:.4f}".format(epoch, loss.tolist()))

    return final_checkpoint_name if "final_checkpoint_name" in vars() else None

def graph_stat(graph, batch_size=5, embedding_dim=50):
    """
    graph - a `rdflib` graph or just an iterable to return triplets
    batch_size - expected batch_size
    embedding_dim - the dimension of the embedding vectors

    return - a URI-id mapping plan, an initiated TransH model, a `tph` & `hpt` statistics, a dataloader
    URI-id mapping plan - a tuple of (nodes mapping, relations mapping)
    """

    nodes = set(itertools.chain.from_iterable((s, o) for s, _, o in graph))
    nodes = dict((n, i) for i, n in enumerate(nodes))
    relations = set(p for _, p, _ in graph)
    relations = dict((r, i) for i, r in enumerate(relations))
    #stat = {r: {n: [0, 0] for n in nodes} for r in relations}
    stat = np.zeros((len(relations), len(nodes), 2))

    for s, p, o in graph:
        stat[relations[p]][nodes[s]][0] += 1
        stat[relations[p]][nodes[o]][1] += 1

    def batch_dataloader(graph, batch_size=5):
        graph = list((nodes[s], relations[p], nodes[o]) for s, p, o in graph)
        while True:
            batch = []
            for i in range(batch_size):
                batch.append(graph[random.randrange(len(graph))])
            yield batch

    node_embedding = np.squeeze(np.asarray(matlib.randn(len(nodes), embedding_dim)))
    node_embedding /= np.sqrt(np.sum(node_embedding**2, axis=1))[:, None]
    relation_embedding = np.reshape(np.asarray(matlib.randn(len(relations), 2*embedding_dim)), (len(relations), 2, embedding_dim))
    relation_embedding[:, 0, :] /= np.sqrt(np.sum(relation_embedding[:, 0, :]**2, axis=1))[:, None]
    return (nodes, relations), (node_embedding, relation_embedding), stat, batch_dataloader(graph, batch_size)
