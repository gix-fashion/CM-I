"""
Composed by Zhand Danyang @THU
Last Revision: Sep 3rd, 2019
"""

import rdflib

_prefix = "http://ch-i.gix-fashion.cn/"

recipe = rdflib.Namespace(_prefix + "recipe#") # 方剂
material = rdflib.Namespace(_prefix + "material#") # 药材
symptom = rdflib.Namespace(_prefix + "symptom#") # 病症
effect = rdflib.Namespace(_prefix + "effect#") # 功效
pathogenisis = rdflib.Namespace(_prefix + "pathogenisis#") # 病理与性质

_prefix = rdflib.Namespace(_prefix)

comprises = _prefix["comprises"] # recipe -> material
major_in = _prefix["majorIn"] # recipe -> symptom, material -> symptom,
has_effect = _prefix["hasEffect"] # recipe -> effect, material -> effect
treatment_plan = _prefix["treatmentPlan"] # symptom -> effect
originates_from = _prefix["originatesFrom"] # symptom -> pathogenisis
applys_on = _prefix["applysOn"] # effect -> pathogenisis
