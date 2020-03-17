"""
Program Title: ScanSphere - Part 1-4
Program Desc: This tool, comprised of four parts, is a network security tool that scans a 
network and assesses its overall security posture. In Part 1, the tool will use nmap to scan a network,
giving the user three scanning options and prepare the raw nmap data for database transfer. Part 2 oversees
the database transfer of the raw data collected in Part 1 and parses the raw data to create nodes (hosts
and attributes) and edges. Part 3 then takes this filtered data and constructs a directed, weighted graph,
after which the tool executes the Structured Deep Network Embedding (SDNE) and node2vec graph embedding
techniques in Part 4.
Authors: Dhivahari Vivek, Turgerel Amgalanbaatar, Hosna Zulali, Kulprawee Prayoonsuk, Katerina Walter
"""

import os
import sys
import nmap
import json
import networkx as nx
import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# GEM Libraries used
import matplotlib.pyplot as plt
from time import time
from gem.utils      import graph_util, plot_util
from gem.evaluation import visualize_embedding as viz
from gem.evaluation import evaluate_graph_reconstruction as gr

# from gem.embedding.node2vec import node2vec
from gem.embedding.sdne     import SDNE

"""
---------------------------------------------------------------------------------------------------------------
Part 1 - NMAP NETWORK SCAN                                                                                  
The tool gives the user three scanning options: scan a single IP address, scan a range of IP addresses, or     
scan several specific IP addresses. It uses Nmap (more specifically, the python-nmap library that helps in    
using the Nmap port scanner) and then prepares the raw nmap data for database transfer.                       
---------------------------------------------------------------------------------------------------------------
"""

# will create local JSON file of parsed NMAP data
def makeJson(nm):
    # creating list of nmap dictionaries
    nmapList = []
    for count in nm.all_hosts():
        nmapOBJ = parseScanDoc(nm,count)
        nmapList.append(nmapOBJ)

    # preparing for JSON transfer
    machine = {}
    # iterating through nmapList to convert each node's data to JSON
    index = 0
    for node in nmapList: # nmapList list of 'machine' dictionaries. machine dictionary key-ip address, value dictionary of values
        machine[nmapList[index]['host_IP']]={
            'host_name': nmapList[index].get('host_name', ""),
            'host_state': nmapList[index].get('host_state', ""),
            'port-details': {
                'all_protocols': nmapList[index].get('all_protocols',""),
                'tcp_open': nmapList[index].get('tcp_open',""),
                'udp_open': nmapList[index].get('udp_open',""),
                'ip_open': nmapList[index].get('ip_open',""),
                'sctp_open': nmapList[index].get('sctp_open',"")
                },
            'os-details': {
                'os_type': nmapList[index].get('os_type',""),
                'os_vendor': nmapList[index].get('os_vend',""),
                'os_family': nmapList[index].get('os_fam',""),
                'os_generation': nmapList[index].get('os_gen',"")
                }
        }
        index+=1
    s = json.dumps(machine, indent=4, sort_keys=True)     # sort_keys = attributes dumped in order
    # formally creating json file to be used for database entry
    with open("nmap_nodes.json","w") as f:
        f.write(s)
#END DEF makejson

# client will select from menu of scan options
def mainmenu():
    menu = int(input("\nMake a selection:\n1. Scan a single IP address.\n2. Scan a range of IP addresses.\n3. Scan different IP addresses.\n\n"))

    # scanning single IP
    if(menu == 1):
        ip = str(input("\nEnter the IP to be scanned: "))
        print("scanning single IP address...")

    # scanning a range of IP
    elif(menu == 2):
        ip = input("\nEnter the range of IP addresses via CIDR notation (example: 192.168.1.0/30): ")
        print("scanning given range of IP addresses...")

    # scanning different IPs
    elif(menu == 3):
        ip = input("\nEnter the IP addresses to be scanned (EACH SEPARATED BY A SINGLE SPACE): ")
        print("scanning entered IP addresses...")
    return ip
#END DEF mainmenu

# will parse the scanned document and create nmap objects for each IP scanned
def parseScanDoc(nm,count):
##IF UPDATED, json function will not match. Make appropriate changes##
    nmapOBJ = {}    # creating empty dictionary for each host
    # data must be parsed differently depending on whether OS info can be collected
    # TODO: as info list expands, change to (IF NULL DONT ADD KEYVALUE PAIR)
    # nm type = <class 'nmap.nmap.PortScanner'>
    # nm[count] type = <class 'nmap.nmap.PortScannerHostDict'>
    if nm[count].hostname():
        nmapOBJ['host_name']=nm[count].hostname() #type str
    if nm[count].state():
        nmapOBJ['host_state']=nm[count].state() #type str
    if nm[count].all_protocols():
        nmapOBJ['all_protocols']=nm[count].all_protocols() #type list
    if nm[count].all_tcp():
        nmapOBJ['tcp_open']=nm[count].all_tcp() #type list
    if nm[count].all_udp():
        nmapOBJ['udp_open']=nm[count].all_udp() #type list
    if nm[count].all_ip():
        nmapOBJ['ip_open']=nm[count].all_ip() #type list
    if nm[count].all_sctp():
        nmapOBJ['sctp_open']=nm[count].all_sctp() #type list
    if 'osmatch' in nm[count]:
        for osmatch in nm[count]['osmatch']:
            if osmatch['osclass'][0]['type']:
                nmapOBJ['os_type']=osmatch['osclass'][0]['type'] #type str
            if osmatch['osclass'][0]['vendor']:
                nmapOBJ['os_vend']=osmatch['osclass'][0]['vendor'] #type str
            if osmatch['osclass'][0]['osfamily']:
                nmapOBJ['os_fam']=osmatch['osclass'][0]['osfamily'] #type str
            if osmatch['osclass'][0]['osgen']:
                nmapOBJ['os_gen']=osmatch['osclass'][0]['osgen'] #type str

    return nmapOBJ
#END DEF parseScanDoc

def customScan(var1, var2):
#TODO: customize the nmap scan run
    return var1,var2

# will conduct the main scan and create a list of documents (for database transfer)
def mainScan(ip):
    print ("Scanning...")
    nm = nmap.PortScanner()
    scanDatetime = datetime.datetime.now()
    # running scans based on IP addresses user entered
    nm.scan(ip, '0-443', arguments='-O')
    # creating list of DOCUMENTS
    print("Consolidating data...")
    nmapList = []
    for count in nm.all_hosts():
        nmapOBJ = parseScanDoc(nm,count)
        mach_doc = {'scanID': scanDatetime, 'hostIP' : count, 'scanData' : nmapOBJ}
        nmapList.append(mach_doc)
    return nmapList
#END DEF mainScan

# will transfer raw nmap data to database as nmapData documents
def rawtoDB(nmapList):
    try:
        #***Send to DB***#
        print("Connecting to database...")
        myclient = MongoClient("mongodb+srv://dbAdmin:dbAdmin123@scandata-fjmex.mongodb.net/test?retryWrites=true&w=majority")
        mydb = myclient.ScanData # database
        mycol = mydb.nmapData
        print("Sending raw NMAP data to database...")
        results = mycol.insert_many(nmapList)
        return results
    except Exception as e:
        print(e)
#END DEF rawtoDB

"""
---------------------------------------------------------------------------------------------------------------
Part 2 - DATABASE COLLECTION, GRAPH NODE/EDGE GENERATION							      
The tool transfers the raw Nmap data collected in Part 1 to a MongoDB server which will store the scanned 
network's data. The data is then sorted into nodes (hosts and attributes) and edges (relationships between 
hosts and attributes) for graph construction in Part 3. See the Graph Construction document to understand 
this process in further detail.
---------------------------------------------------------------------------------------------------------------
"""

# will increment the counter to generate numerical IDs for human-readable nodes and edges 
def incrementCounter(myCounter):
    x = myCounter.find_one()    # found the counter
    temp = x['counter']
    temp += 1        # increment counter - which is the index of the node
    x1 = { "$set": { "counter" : temp}}
    new_x = myCounter.update_one(x,x1)     # update
    return 0
#END DEF incrementCounter

# will create attribute nodes (database documents of node type "A")
def createAttr(attr,value,myATT,myNODES, myCounter):
    print("Creating attribute document...")
    print("Attr:", attr, "value:", value)
    # creating new attribute document
    attDoc = { "att_key": attr, "att_val": value }
    a = myATT.insert_one(attDoc)
    # create a node doc of type (A)ttribute
    print("Connecting attribute --> node type A...")
    b = myCounter.find_one()
    nodeDoc = {'num_ID': b['counter'], "node_type": "A", "ref_ID": a.inserted_id}
    incrementCounter(myCounter)
    
    print("Created attribute node.")
    c = myNODES.insert_one(nodeDoc)
    print("Inserted attribute node.")
    return c
#END DEF createAttr

# will be part of the check for existing attribute nodes (nodes of type "A")
def compareAll(attr,value,myATTdoc):
    if type(attr) == type (myATTdoc["att_key"]):
        # do normal check
        if attr == myATTdoc["att_key"]:
            if type(value) == type(myATTdoc["att_val"]):
                # do normal check
                if value == myATTdoc["att_val"]:
                    return True # iff all match
                else:
                    return False
                
            else:
                print("Fix type compare 1")
                # fix type compare
        else:
            return False
    else:
        print("Fix type compare 2")
        # fix type compare
    
    return False
#END DEF compareAll

# will determine edge weight 
def edgeWeight():
    return 1
#END DEF edgeWeight

# will create edges via edge database documents
def createEdge(src,des):
    print()
    print("Creating new edge...")
    weight = edgeWeight()
    edgeDoc = {'node1': src, 'node2':des, 'weight': weight}
    return edgeDoc
#END DEF createEdge

# will connect to database to populate the nodes 
def populateHostNode():
    try:
        # establishing connection
        print("Connecting to database - populating host nodes...")
        myClient = MongoClient("mongodb+srv://dbAdmin:dbAdmin123@scandata-fjmex.mongodb.net/test?retryWrites=true&w=majority")
        myDB = myClient.ScanData    # accesses database
        
        myNMAP = myDB.nmapData          # accesses raw data (nmapData collection)
        myNODES = myDB.nodes        # accesses nodes (nodes collection)
        myATT = myDB.attributes         # accesses attributes (attributes collection)
        myEDGES = myDB.edges        # accesses edges (edges collection)
        myCounter = myDB.counter
        
        myNODES.drop()  # clearing host nodes each run (for new scan)
        myNODES.create_index("num_ID")
        myATT.drop()    # clearing attribute docs
        myEDGES.drop()  # clearing edges doc

        print ("Creating host nodes...")
        # iterating through nmapList collection (raw data)
        for x in myNMAP.find():
            a = myCounter.find_one()
            a_val = a['counter']
            myDoc = {'num_ID': a_val, "node_type": "H", "ref_ID": x['_id'] }
            print(myDoc)
            incrementCounter(myCounter)
            y = myNODES.insert_one(myDoc)       # inserting this document into Nodes Collection

        # iterating through host nodes in node collection
        for x in myNODES.find({"node_type":"H"}):
            myQuery = { "_id": x['ref_ID']}     # accessing nmapData via host node's reference ID
            myNMAPdoc = myNMAP.find_one(myQuery)   # temporarily saving the NMAP doc in question
            scanData = myNMAPdoc.get("scanData")    # retrieving attributes from each nmap node
            # for each pair of attributes
            print()
            print("Checking for attribute values...")
            dest = '' #object id
            for attr, value in scanData.items():   #attr,value of nmapData for each H type node
                # for each Node document of type (A)ttribute
                # compare against existing nodes for this exact combo
                results = myNODES.find({"node_type":"A"})
                print()
                print("Searching through attribute node results...len:", myNODES.count_documents({"node_type":"A"}))
                counter = 0
                isFound = False
                for res in results:
                    counter+=1
                    nodeQuery = {"_id": res["ref_ID"]}    # accessing attribute doc via att node's reference ID
                    myATTdoc = myATT.find_one(nodeQuery)   # temporarily saving the ATTR doc in question
                    
                    if compareAll(attr,value,myATTdoc): #if T.E. A type node with attr,value, no action needed
                        print("Compare = True - Attribute match found!")
                        dest = res['_id']
                        isFound = True
                        break
                if not isFound:
                    print("Compare = False - Creating new attribute node...")
                    result = createAttr(attr,value,myATT,myNODES,myCounter)
                    dest = result.inserted_id
                    print(result, attr, value) #print resulting A type node
                    
                # making edges
                print(type(x['_id']))
                print("Creating new edge...")
                b = myNODES.find_one({"_id":dest})
                newEdge = createEdge(x['num_ID'],b['num_ID'])
                #TODO CHANGE TO ENUMERATION CODES INSTEAD
                print(type(newEdge),newEdge)
                edgeResult = myEDGES.insert_one(newEdge)
                print()
                print(edgeResult)
            
                    
               
    except Exception as e:
      print(e)
#END DEF populateHostNode

def main():
    try:
        ip = mainmenu() # get IP(s) to scan
        nmapList = mainScan(ip) # nmapList is list of Documents (hostIP, Values<dict>) to import
        results = rawtoDB(nmapList) # send scanned data to DB
        
    except Exception as e:
        print(e)

    try:
        # populating nodes of type (H)ost
        populateHostNode()
    except Exception as e:
        print(e)
#END DEF main

main()

"""
---------------------------------------------------------------------------------------------------------------
Part 3 - GRAPH CONSTRUCTION										      
The nodes and edges generated in Part 2 will be used to construct a directed, unweighted graph (using 
Python's NetworkX library).
---------------------------------------------------------------------------------------------------------------
"""
# DiGraph is a base class for directed graphs (stores directed edges)
G = nx.DiGraph()

# establishing connection
print("\nConstructing graph...")

myClient = MongoClient("mongodb+srv://dbAdmin:dbAdmin123@scandata-fjmex.mongodb.net/test?retryWrites=true&w=majority")
myDB = myClient.ScanData    # accesses database

myNMAP = myDB.nmapData  # accesses raw data (nmapData collection)
myNODES = myDB.nodes    # accesses nodes (nodes collection)
myATT = myDB.attributes # accesses attributes (attributes collection)
myEDGES = myDB.edges    # accesses edges (edges collection)

# iterating through the NODES collection to scale the nodes
numID_arr = []
for n in myNODES.find():
    numID_arr.append(n['num_ID'])

numID_arr.sort()
lowest_val = numID_arr[0]

# iterating through the EDGES collection
for e in myEDGES.find():
    host_node = e['node1']  # the object ID to the host node of the edge
    att_node = e['node2']   # the object ID to the att node of the edge
    host_node = host_node - lowest_val
    att_node = att_node - lowest_val
    w = e['weight']    # the weight of the edge - type INT
    G.add_edge(host_node, att_node, weight=w)

print("\nThe total number of nodes is: ", G.number_of_nodes(),'\n')


"""
-------------------------------------------------------------------------------------------------------------------
Part 4 - GRAPH EMBEDDING METHODS (GEM)										  
The tool will then execute the Structured Deep Network Embedding (SDNE) and node2vec graph embedding techniques
(using the GEM library).
-------------------------------------------------------------------------------------------------------------------
"""

# File that contains the edges. Format: source target
# Optionally, you can add weights as third column: source target weight
kf = open('data/karate.edgelist', 'wb')
nx.write_edgelist(G, kf, data=['weight'])

edge_f = 'data/karate.edgelist'
# Specify whether the edges are directed
isDirected = True

# Load graph
# G = graph_util.loadGraphFromEdgeListTxt(edge_f, directed=isDirected)
G = G.to_directed()

models = []
# models.append(node2vec(d=2, max_iter=1, walk_len=80, num_walks=10, con_size=10, ret_p=1, inout_p=1))
models.append(SDNE(d=2, beta=5, alpha=1e-5, nu1=1e-6, nu2=1e-6, K=3,n_units=[50, 15,], rho=0.3, n_iter=50, xeta=0.01,n_batch=100,
                modelfile=['enc_model.json', 'dec_model.json'],
                weightfile=['enc_weights.hdf5', 'dec_weights.hdf5']))

# For each model, learn the embedding and evaluate on graph reconstruction and visualization
for embedding in models:
    print ('Num nodes: %d, num edges: %d' % (G.number_of_nodes(), G.number_of_edges()))
    t1 = time()
    # Learn embedding - accepts a networkx graph or file with edge list
    Y, t = embedding.learn_embedding(graph=G, edge_f=None, is_weighted=True, no_python=True)
    print (embedding._method_name+':\n\tTraining time: %f' % (time() - t1))
    # Evaluate on graph reconstruction
    MAP, prec_curv, err, err_baseline = gr.evaluateStaticGraphReconstruction(G, embedding, Y, None)
    #---------------------------------------------------------------------------------
    print(("\tMAP: {} \t precision curve: {}\n\n\n\n"+'-'*100).format(MAP,prec_curv[:5]))
    #---------------------------------------------------------------------------------
    # Visualize
    viz.plot_embedding2D(embedding.get_embedding(), di_graph=G, node_colors=None)
    plt.show()
    plt.clf()

