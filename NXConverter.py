import xml.etree.ElementTree as ET
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, DCTERMS, XSD
import xml.dom.minidom as md

import matplotlib.pyplot as plt
import japanize_matplotlib 

import networkx as nx
from IPython.display import set_matplotlib_formats

def ttl_to_networkx(g_nx, ttlpath):
  pd3 = Namespace('http://DigitalTriplet.net/2021/08/ontology#')
  g_ttl = Graph()
  g_ttl.parse(ttlpath)

  for s, p, o in g_ttl.triples((None, RDF.type, None)):
    if(o == pd3.EngineeringProcess):
      creator, title, description, identifier = '', '', '', ''
      for s1, p1, o1 in g_ttl.triples((s, None, None)):
        if(p1 == DCTERMS.creator):
          creator = str(o1)
        elif(p1 == DCTERMS.title):
          title = str(o1)
        elif(p1 == DCTERMS.description):
          description = str(o1)
        elif(p1 == DCTERMS.identifier):
          identifier = str(o1)
        elif(p1 == pd3.use):
          g_nx.add_edge(s, o1)
        elif(p1 == pd3.useBy):
          g_nx.add_edge(s, o1)
      g_nx.add_node(s)
      g_nx.nodes[s]['creator'] = creator
      g_nx.nodes[s]['title'] = title
      g_nx.nodes[s]['description'] = description
      g_nx.nodes[s]['identifier'] = identifier

    if(o == pd3.Action):
      # 2022/3/7 mod Start Man
      actionType, value, id, layer, use, useby = None, None, None, None, None, None
      use = []
      useby = []
      # 2022/3/7 mod End Man
      for s1, p1, o1 in g_ttl.triples((s, None, None)):
        if(p1 == pd3.actionType):
          actionType = str(o1)
        elif(p1 == pd3.value):
          value = str(o1)
        elif(p1 == pd3.layer):
          layer = str(o1)
        elif(p1 == pd3.id):
          id = str(o1)
        # 2022/3/7 mod Start Man
        elif(p1 == pd3.use):
          use.append(o1)
        elif (p1 == pd3.useBy):
          useby.append(o1)
        # 2022/3/7 mod End Man
      g_nx.add_node(s)
      g_nx.nodes[s]['type'] = 'Action'
      g_nx.nodes[s]['actionType'] = actionType
      g_nx.nodes[s]['value'] = value
      g_nx.nodes[s]['layer'] = layer
      g_nx.nodes[s]['id'] = id

      # Use, UseBy関係性処理
      # 2022/3/7 mod Start Man
      for i in range(len(use)):
          #print(seealso[i])
          g_nx.add_edge(s, use[i])
      for i in range(len(useby)):
          g_nx.add_edge(s, useby[i])
      # 2022/3/7 mod End Man

    # 2022/1/11 add Start Man
    if(o == pd3.Object):
      value, id, layer = None, None, None
      for s1, p1, o1 in g_ttl.triples((s, None, None)):
        if(p1 == pd3.value):
          value = str(o1)
        elif(p1 == pd3.layer):
          layer = str(o1)
        elif(p1 == pd3.id):
          id = str(o1)
      g_nx.add_node(s)
      g_nx.nodes[s]['type'] = 'Object'
      g_nx.nodes[s]['value'] = value
      g_nx.nodes[s]['layer'] = layer
      g_nx.nodes[s]['id'] = id
      # 2022/1/11 add End Man

    if(o == pd3.Container):
      # 2022/1/11 add Start Man
      value, id, layer, output = None, None, None, None
      # 2022/1/11 add End Man
      member = []
      output = []
      for s1, p1, o1 in g_ttl.triples((s, None, None)):
        if(p1 == pd3.member):
          member.append(o1)
      # 2022/04/01 Mod Start Man
        if(p1 == pd3.output):
          output.append(o1)

      """
      # 2022/1/12 Mod Start Man
        elif(p1 == pd3.id):
          id = str(o1)
        elif(p1 == pd3.layer):
          layer = str(o1)
        elif(p1 == pd3.value):
          value = str(o1)

      if(len(member) == 0):
        g_nx.add_node(s)
        g_nx.nodes[s]['type'] = 'Container'
        g_nx.nodes[s]['id'] = id
        g_nx.nodes[s]['value'] = value
        g_nx.nodes[s]['layer'] = layer
      # 2022/1/12 Mod End Man
      """
      for node in output:
        for i in range(len(member)):
          g_nx.add_edge(node, member[i])
          g_nx.edges[node, member[i]]['arcType'] = 'member'
          g_nx.edges[node, member[i]]['layer'] = 'layer'
      # 2022/04/01 Mod End Man

    if(o == pd3.Flow):
      # 2022/1/11 add Start Man
      value, target, source, id, layer = None, None, None, None, None
      # 2022/1/11 add End Man
      for s1, p1, o1 in g_ttl.triples((s, None, None)):
        if(p1 == pd3.target):
          target = o1
        elif(p1 == pd3.source):
          source = o1
        elif(p1 == pd3.value):
          value = str(o1)
        elif(p1 == pd3.layer):
          layer = str(o1)
        elif(p1 == pd3.id):
          id = str(o1)
      g_nx.add_edge(source, target)
      g_nx.edges[source, target]['arcType'] = 'information'
      g_nx.edges[source, target]['value'] = value
      g_nx.edges[source, target]['layer'] = layer
      g_nx.edges[source, target]['id'] = id

    """
    if(o == pd3.ContainerFlow):
      # 2022/1/11 add Start Man
      arcType, value, target, source, id, layer = None, None, None, None, None, None
      # 2022/1/11 add End Man
      for s1, p1, o1 in g_ttl.triples((s, None, None)):
        if(p1 == pd3.arcType):
          arcType = str(o1)
        elif(p1 == pd3.id):
          id = str(o1)
        elif(p1 == pd3.layer):
          layer = str(o1)
        elif(p1 == pd3.value):
          value = str(o1)
        elif(p1 == pd3.source):
          source = o1
        elif(p1 == pd3.target):
          target = o1
      # 2022/1/11 add Start Man
      if(layer == 'topic'):
      # 2022/1/11 add End Man
        g_nx.add_edge(source, target)
        g_nx.edges[source, target]['arcType'] = 'hierarchization'
        g_nx.edges[source, target]['value'] = value
        g_nx.edges[source, target]['layer'] = layer
        g_nx.edges[source, target]['id'] = id
    """

    if(o == pd3.SupFlow):
      # 2022/1/11 Mod Start Man
      arcType, value, target, source, id, layer = None, None, None, None, None, None
      for s1, p1, o1 in g_ttl.triples((s, None, None)):
        if(p1 == pd3.arcType):
          arcType = str(o1)
        elif(p1 == pd3.value):
          value = str(o1)
        elif(p1 == pd3.target):
          target = o1
        elif(p1 == pd3.source):
          source = o1
        elif(p1 == pd3.id):
          id = str(o1)
        elif(p1 == pd3.layer):
          layer = str(o1)

      if (source != None):
        g_nx.add_edge(source, target)
        g_nx.edges[source, target]['arcType'] = 'tool/knowledge'
        g_nx.edges[source, target]['value'] = value
        g_nx.edges[source, target]['layer'] = layer
        g_nx.edges[source, target]['id'] = id
      else:
        g_nx.add_node(target)
        g_nx.nodes[target][arcType] = value
      # 2022/1/11 mod End Man
  

