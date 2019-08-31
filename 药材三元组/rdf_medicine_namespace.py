import rdflib

_prefix = "http://ch-i.gix-fashion.cn/"
_prefix = rdflib.Namespace(_prefix)

medicine = rdflib.Namespace(_prefix + "medicine#") # 药材名
m_effect = rdflib.Namespace(_prefix + "m_effect#") # 药材功效
major_function = rdflib.Namespace(_prefix + "major_function#") # 药材主治

has_effect = _prefix["hasEffect"] # medicine has_effect m_effect
major_in = _prefix["majorIn"] # medicine major_in major_function
