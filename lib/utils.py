"""
Several functions to handle strings.

Composed by Zhand Danyang @THU
Last Revision: Aug 22nd, 2019
"""

import re
import math
import numpy as np

import concurrent.futures as con

_utf8_pat = re.compile("((%[A-Z0-9]{2})+)")

def format_url_keyword(url_keyword):
    """
    Format a string like "%E4%BD%A0%E5%A5%BD" to a string like "你好".

    return a converted string.
    """

    mat = _utf8_pat.findall(url_keyword)
    utf8_parts = [m[0] for m in mat]
    utf8_encodes = (p.replace("%", "") for p in utf8_parts)
    utf8_decodes = (str(bytes.fromhex(p), encoding="utf-8") for p in utf8_encodes)

    for op, de in zip(utf8_parts, utf8_decodes):
        url_keyword = url_keyword.replace(op, de)

    return url_keyword

_white_space_pat = re.compile(r"\s+")
remove_white_spaces = lambda string: _white_space_pat.sub("", string) # return the string with all the white spaces removed

_combination_pat = re.compile(r"\s*\+\s*")
_substitution_pat = re.compile(r"\s*\/\s*")

def format_recipe_from_str_to_list(recipe):
    """
    recipe - a string with medicine material connected with "+" or "/"

    return a list, with elements as list of str or str
    """

    recipe = _combination_pat.split(recipe)
    recipe = (_substitution_pat.split(r) if "/" in r else r for r in recipe)
    result = []
    for r in recipe:
        if type(r)==str:
            result.append(remove_white_spaces(r))
        else:
            result.append([remove_white_spaces(u) for u in r])
    return result

_equivalence_pat = re.compile(r"\s*[=/]\s*")
_equivalence_entry_pat = re.compile(r"^\s*([^()（）]*)(?:[(（]([^()（）]+)[)）])?([^()（）]*)\s*$")
_equivalence_pat2 = re.compile(r"\s*[、,.，]\s*")

def extract_equivalent_expressions(name):
    """
    Extract the equivalent expressions.

    return a single str or a tuple of str
    """

    parts = (p.strip() for p in _equivalence_pat.split(name) if p.strip()!="")
    names = []
    for n in parts:
        mat = _equivalence_entry_pat.match(n)
        first = remove_white_spaces(mat.group(1))
        others = mat.group(2)
        residual = mat.group(3)

        names.append(first + residual)

        if others is not None:
            others = _equivalence_pat2.split(others)
            others = (s + residual if len(s)>1 else first + s + residual for s in others)
            others = (remove_white_spaces(s) for s in others)
            names += others
    return names

#_clause_split_pat = re.compile(r"(?<=[^a-zA-Z0-9])\d+\s*[.、）),，．]\s*")
_clause_split_pat = re.compile(r"(?:\d+\s*[.、）),，．]|\(\d+\)|（\d+）)\s*")
_chinese_period_pat = re.compile(r"(?<=。)\s*")

def divide_into_sentences(string):
    """
    return a list of str
    """

    sentences = _clause_split_pat.split(string) if _clause_split_pat.search(string) is not None\
            else _chinese_period_pat.split(string)
    sentences = (s.strip() for s in sentences)
    sentences = [s for s in sentences if len(s)>0]
    return sentences

def edit_distance(str1, str2):
    """
    Calculate the conventional edit distance considering three kinds of actions - insertion, deletion and replacement.

    return the edit distance
    """

    l1 = len(str1)
    l2 = len(str2)
    dis = np.zeros((l1+1, l2+1), dtype=np.int32)

    dis[0, :] = np.arange(0, l2+1)
    dis[:, 0] = np.arange(0, l1+1)
    for i in range(1, l1+1):
        for j in range(1, l2+1):
            dis[i, j] = dis[i-1, j-1] if str1[i-1]==str2[j-1]\
                    else min(dis[i-1, j], dis[i, j-1], dis[i-1, j-1])+1

    return dis[-1, -1]

#special_identical_names = []
#special_different_names = []
special_identical_names = [
        ("芒硝", "玄明粉"),
        ("木蝴蝶", "千层纸")
]
special_different_names = [
        ("五味子", "五倍子"),
        ("紫珠叶", "紫苏叶"),
        ("紫苏叶", "苏子"),
        ("冬瓜子", "南瓜子"),
        ("冬瓜子", "冬葵子"),
        ("冬葵子", "天葵子"),
        ("天葵子", "天仙子"),
        ("地耳草", "地锦草"),
        ("苎麻根", "蓖麻根", "茼麻子", "亚麻子"),
        ("草乌", "川乌"),
        ("药子", "芥子", "附子")
]
# these list should be set if the special rules for `is_identical` function should be used

def is_identical(drug1, drug2, dist_thrd=0.34):
    """
    drug1 - str
    drug2 - str
    dist_thrd - the threshold of edit distance; if the d(drug1, drug2) <= dist_thrd*max{len(drug1), len(drug2)}, `drug1` and `drug2` will be considered as the factual identical drug

    return True of False
    """

    max_dist = len(drug1) + len(drug2)
    dist_thrd = math.floor(dist_thrd*max(len(drug1), len(drug2)))

    def test_special_identity_rules():
        rule_hit = lambda ss: any(edit_distance(drug1, d)<=dist_thrd for d in ss) and\
                any(edit_distance(drug2, d)<=dist_thrd for d in ss)

        #pool = con.ThreadPoolExecutor()
        #futures = (pool.submit(rule_hit, ss) for ss in special_identical_names)
        #results = (f.result() for f in futures)
        results = (rule_hit(ss) for ss in special_identical_names)
        return any(results)

    def test_special_difference_rules():
        def rule_hit(ss):
            index1 = None
            min_dist1 = max_dist
            index2 = None
            min_dist2 = max_dist
            for i, d in enumerate(ss):
                dist1 = edit_distance(drug1, d)
                dist2 = edit_distance(drug2, d)
                if dist1<=dist_thrd and dist1<min_dist1:
                    index1 = i
                    min_dist1 = dist1
                if dist2<=dist_thrd and dist2<min_dist2:
                    index2 = i
                    min_dist2 = dist2
            return index1, index2

        #pool = con.ThreadPoolExecutor()
        #futures = (pool.submit(rule_hit, ss) for ss in special_different_names)
        #results = (f.result() for f in futures)
        results = (rule_hit(ss) for ss in special_different_names)
        results = (not (i1 is not None and i2 is not None and i1!=i2) for i1, i2 in results)
        #results = list(results)
        #print(results)
        return all(results)

    test_conventional_rules = lambda: edit_distance(drug1, drug2)<=dist_thrd

    indicators = con.ThreadPoolExecutor()
    sirf = indicators.submit(test_special_identity_rules)
    sdrf = indicators.submit(test_special_difference_rules)
    crf = indicators.submit(test_conventional_rules)

    #print(sirf.result())
    #print(sdrf.result())
    #print(crf.result())

    return sirf.result() or sdrf.result() and crf.result()

def is_identical_for_iterable(single_drug, drug_iter, dist_thrd=0.34):
    """
    This function is used for the situation that one of the parameter is an iterable.

    single_drug - str
    drug_iter - iterable
    dist_thrd - the threshold of edit distance; if the d(drug1, drug2) <= dist_thrd*max{len(drug1), len(drug2)}, `drug1` and `drug2` will be considered as the factual identical drug
    """

    indicators = con.ThreadPoolExecutor()
    futures = (indicators.submit(is_identical, single_drug, ad, dist_thrd) for ad in drug_iter)
    results = (f.result() for f in futures)
    return any(results)
