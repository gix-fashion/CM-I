import rdflib
import rdf_medicine_namespace as ns
import os
import json

graph = rdflib.Graph()

for root, dirs, files in os.walk('D:\\workspace\\knowledgegraph\\tri\\data'):
	for file in files:
		file = open('D:\\workspace\\knowledgegraph\\tri\\data\\'+file, 'r', encoding='gb18030')
		medicine_dict = json.load(file)
		graph.add((ns.medicine[medicine_dict['药材名']],
					ns.has_effect, ns.m_effect[medicine_dict['功效']]))
		graph.add((ns.medicine[medicine_dict['药材名']],
					ns.major_in, ns.major_function[medicine_dict['主治']]))

graph.serialize(destination="subgraph_medicine", format="xml")

