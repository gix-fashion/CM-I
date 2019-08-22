#!/usr/bin/python3

"""
Check the IoU of the keywords in different databases.

Composed by Zhand Danyang @THU
"""

import sys
sys.path.insert(0, "../../")

import utils
import json
import itertools
import copy

class DiseaseName:
    def __init__(self, name_str):
        if isinstance(name_str, str):
            self._name = name_str
            self._names = utils.extract_equivalent_expressions(name_str)
        elif hasattr(name_str, "__iter__"):
            self._name = "/".join(name_str)
            self._names = list(name_str)

    @property
    def names(self):
        return self._names

    def __eq__(self, other):
        if isinstance(other, str):
            other = utils.extract_equivalent_expressions(other)
        elif isinstance(other, DiseaseName):
            other = other.names
        elif hasattr(other, "__iter__"):
            other = list(other)
        else:
            raise TypeError

        for m in self._names:
            for n in other:
                if m==n:
                    return True
        return False

    def __hash__(self):
        return hash(self._name)

    def __str__(self):
        return str(self._names)

    def __repr__(self):
        return "DiseaseName({:})".format(self._names)

    @staticmethod
    def intersection(list1, list2):
        """
        list1 - list of DiseaseName
        list2 - list of DiseaseName

        return a set of the intersection of list1 and list2
        """

        intersection = set()
        for d in list1:
            for q in list2:
                if d==q:
                    intersection.add(d)
                    intersection.add(q)
        return intersection

    @staticmethod
    def iou(list1, list2):
        """
        list1 - list of DiseaseName
        list2 - list of DiseaseName

        return the IoU of list1 and list2
        """

        intersection = DiseaseName.intersection(list1, list2)
        intersection = len(intersection)
        union = len(list1)+len(list2)-intersection

        return intersection/float(union)

if __name__ == "__main__":
    with open("常见病汇总.json") as f:
        baseline = itertools.chain.from_iterable(json.load(f).values())
        baseline = [DiseaseName(n) for n in baseline]
        #print(baseline)

    paedias = [None for i in range(3)]
    with open("全面!114种常见疾病联合用药方案大全.json") as f:
        dict1 = json.load(f).keys()
        paedias[0] = [DiseaseName(n) for n in dict1]
        #print(paedias[0])

    with open("常见疾病典型病症资料.json") as f:
        dict2 = json.load(f)
        dict2 = (d.keys() for d in dict2.values())
        paedias[1] = [DiseaseName(n) for n in itertools.chain.from_iterable(dict2)]
        #print(paedias[1])

    with open("中医常见病症.json") as f:
        dict3 = json.load(f)["常见病"].keys()
        paedias[2] = [DiseaseName(n) for n in dict3]
        #print(paedias[2])

    print(len(baseline))
    for p in paedias:
        print(len(p))

# TODO: compute IoU
#for i, d in enumerate(paedias):
        #print("{:d}: {:.4f}".format(i, DiseaseName.iou(baseline, d)))
#
#for d1, d2 in itertools.combinations(paedias, 2):
        #print("{:d}: {:.4f}".format(i, DiseaseName.iou(d1, d2)))
