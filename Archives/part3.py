"""
Program Title: ScanSphere - Part 3
Program Desc: This program implements the specifications of ScanSphere - Part 3, which 
takes from the EDGES collection (database) populated in Part 2, creates an actual graph, and
executes graph embedding functions via the GEM library (namely the node2vec and SDNE).
Authors: Dhivahari Vivek, Turgerel Amgalanbaatar, Hosna Zulali, Kulprawee Prayoonsuk, Katerina Walter
"""

import os
import sys
import json
import datetime
import networkx as nx
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

"""----------GRAPH CONSTRUCTION----------"""
# DiGraph is a base class for directed graphs (stores directed edges)
G = nx.DiGraph()

# establishing connection
print("Connecting to database...")

myClient = MongoClient("mongodb+srv://dbAdmin:dbAdmin123@scandata-fjmex.mongodb.net/test?retryWrites=true&w=majority")
myDB = myClient.ScanData	# accesses database

myNMAP = myDB.nmapData  # accesses raw data (nmapData collection)
myNODES = myDB.nodes    # accesses nodes (nodes collection)
myATT = myDB.attributes # accesses attributes (attributes collection)
myEDGES = myDB.edges    # accesses edges (edges collection)

# iterating through the EDGES collection
for e in myEDGES.find():
    host_node = e['node1']  # the object ID to the host node of the edge
    att_node = e['node2']   # the object ID to the att node of the edge
    w = e['weight']    # the weight of the edge - type INT
    G.add_edge(host_node, att_node, weight = w)

# for DEMO --> printing each edge's end nodes and weight
for u, v, weight in G.edges(data='weight'):
    if weight is not None:
        print("Host node:", u, " Att node:", v, " weight:", weight)
        

print("\nThe total number of nodes is: ", G.number_of_nodes(),'\n')
