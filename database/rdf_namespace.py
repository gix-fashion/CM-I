"""
Composed by Zhand Danyang @THU
Last Revision: Aug 28th, 2019
"""

import rdflib

_prefix = "http://ch-i.gix-fashion.cn/"
_prefix = rdflib.Namespace(_prefix)

recipe = rdflib.Namespace(_prefix + "recipe#")
effect = rdflib.Namespace(_prefix + "effect#")
symptom = rdflib.Namespace(_prefix + "symptom#")
pathogenisis = rdflib.Namespace(_prefix + "pathogenisis#")

has_effect = _prefix["hasEffect"] # recipe -> effect
applys_on = _prefix["applysOn"] # recipe -> symptom, effect -> pathogenisis
treatment_plan = _prefix["treatmentPlan"] # symptom -> effect
originates_from = _prefix["originatesFrom"] # symptom -> pathogenisis
