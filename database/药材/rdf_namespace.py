import rdflib

_prefix = "http://ch-i.gix-fashion.cn/"
_prefix = rdflib.Namespace(_prefix)

recipe = rdflib.Namespace(_prefix + "recipe#")
effect = rdflib.Namespace(_prefix + "effect#")
symptom = rdflib.Namespace(_prefix + "symptom#")

# these three maybe had better be URIRef? TODO
has_effect = _prefix["hasEffect"] # recipe -> effect
treatment_plan = _prefix["treatmentPlan"] # symptom -> effect
applys_on = _prefix["applysOn"] # recipe -> symptom
