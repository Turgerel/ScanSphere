
import os
import sys
import nmap
import json
import networkx as nx
import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


# K-Means Clustering Libraries used
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

# GEM Libraries used
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from time import time
from gem.utils      import graph_util, plot_util
from gem.evaluation import visualize_embedding as viz
from gem.evaluation import evaluate_graph_reconstruction as gr

# from gem.embedding.node2vec import node2vec
from gem.embedding.sdne     import SDNE

################### GUI methods #######################
#global figure saves
#sdne_fig = plt.figure()

def show_entry_fields(e1, ipInputType):
    print("IPADDRESS: %s\nSCANCHOICE:%d" % (e1.get(),ipInputType.get()))
def show_nmap_retrieval(nmaplist):
    print("Raw nmap data:\n")
    print(results)
def init_scan(nmaplist,e1):
    print("Scanning\n")
    nmaplist = mainScan(e1.get())
    results = rawtoDB(nmaplist) # send scanned data to DB
def build_graph(G):
    populateNodes()
    G = define_G(G)
def print_edges(G):
    print(G.edges())
def write_edges(G):
    fh=open("test.edgelist",'wb')
    nx.write_edgelist(G, "test.edgelist", data=['weight'])
def load_graph(G,models):
    fh=open("test.edgelist",'wb')
    edge_f = 'test.edgelist'
    models=load_models(G,edge_f,models)
    sdne_fig=plt.gcf()
    sdne_fig.show()
#def show_SDNE():
#    sdne_fig.show()
def build_elbow(models, new_data):
    print (models)
    elbow_method(models,new_data) #returns list type
    print("build elbow type\n")
    print(type(new_data)) #LIST
    
    return new_data
def calc_k(new_data):
    print("calc k type\n")
    print(type(new_data)) #list
    kmeans(new_data)
    print("calc k  2 type\n") #list
    print(type(new_data))
    elbow_fig = plt.gcf()
    elbow_fig.show()
def show_clusters(str_k,new_data):
    new_data = np.array(new_data)
    k = int(str_k)
    print(type(k),k)
    print(type(str_k),str_k)
    print(type(new_data), new_data) #np
    cluster(k, new_data)
    cluster_fig = plt.gcf()
    cluster_fig.show()
    
    

####################PART 1 methods ######################

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
def mainScan(ip): #type int
    print ("Scanning...")
    nm = nmap.PortScanner()
    scanDatetime = datetime.datetime.now()
    # running scans based on IP addresses user entered
    nm.scan(ip, '0-443', arguments='-O')
    #if int =1:
        #scan(ip, "0-443', arg ='-O')
    #scan(ip, "0-443', arg ='-verbose ')
    
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

################## PART 2 ###########################

    
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
def edgeWeight(attName):
    return 1
#END DEF edgeWeight

# will create edges via edge database documents
def createEdge(src,des,attName):
    print()
    print("Creating new edge...")
    #pass in attribute des
    weight = edgeWeight(attName)
    edgeDoc = {'node1': src, 'node2':des, 'weight': weight}
    return edgeDoc
#END DEF createEdge

# will connect to database to populate the nodes 
def populateNodes():
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

        #EMPTY OLD DATA - keep attributes and A nodes. Keep raw data.
        #print("Clearing previous edges and nodes \n")
        myEDGES.drop()
        #delx= myNODES.delete_many({"node_type":"H"})
        #print("H nodes deleted:",delx.deleted_count)
        
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
                ##Add search for BattName
                BattName = ""
                newEdge = createEdge(x['num_ID'],b['num_ID'],BattName)
                print(type(newEdge),newEdge)
                edgeResult = myEDGES.insert_one(newEdge)
                print()
                print(edgeResult)
            
                    
               
    except Exception as e:
      print(e)
#END DEF populateNodes

################## PART 3 ########################
# DiGraph is a base class for directed graphs (stores directed edges)
def define_G(G):
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
        #if 
        G.add_edge(host_node, att_node, weight=w)

    print("\nThe total number of nodes is: ", G.number_of_nodes(),'\n')
    return G

################## PART 4 TEMP ##################

def load_models(G,edge_f,models):
    isDirected = True

    # Load graph
    G = G.to_directed()

    # models.append(node2vec(d=2, max_iter=1, walk_len=80, num_walks=10, con_size=10, ret_p=1, inout_p=1))
    models.append(SDNE(d=2, beta=5, alpha=1e-5, nu1=1e-6, nu2=1e-6, K=3,n_units=[50, 15,], rho=0.3, n_iter=50, xeta=0.01,n_batch=100,
                    modelfile=['enc_model.json', 'dec_model.json'],
                    weightfile=['enc_weights.hdf5', 'dec_weights.hdf5']))
#    return models,edge_f

    # For each model, learn the embedding and evaluate on graph reconstruction and visualization
    for embedding in models:
        print ('Num nodes: %d, num edges: %d' % (G.number_of_nodes(), G.number_of_edges()))
        t1 = time()
        # Learn embedding - accepts a networkx graph or file with edge list
        Y, t = embedding.learn_embedding(graph=G, edge_f=None, is_weighted=True, no_python=True)
#        Y, t = embedding.learn_embedding(graph=None, edge_f=edge_f, is_weighted=True, no_python=True)

        print (embedding._method_name+':\n\tTraining time: %f' % (time() - t1))
        # Evaluate on graph reconstruction
        MAP, prec_curv, err, err_baseline = gr.evaluateStaticGraphReconstruction(G, embedding, Y, None)###HERE
        #---------------------------------------------------------------------------------
        print(("\tMAP: {} \t precision curve: {}\n\n\n\n"+'-'*100).format(MAP,prec_curv[:5]))
        # ---------------------------------------------------------------------------------
        # Visualize
        viz.plot_embedding2D(embedding.get_embedding(), di_graph=G, node_colors=None)
        #plt.show()
        return models
        
def elbow_method(models,new_data):
    for embedding in models:
        print("I AM RUNNING")
        a = embedding.get_embedding()   # our cluster points as an ndarray

        # cluster points as list (a bit of a hassle since iterating through ndarrays is a b-word
        cluster_list = []
        counter = 0
        # iterating through np.ndarray to list
        for x in np.nditer(a):
            cluster_list.append(x[()])

        # cluster x and y points
        cluster_x = []
        cluster_y = []
        cluster_x = cluster_list[::2]
        cluster_y = cluster_list[1::2]

        #new_data = []
        i = 0
        while i < len(cluster_x):
            x = cluster_x[i]
            y = cluster_y[i]
            new_data.append([x, y])
            i += 1
        #new_data = np.array(new_data)
        print(type(new_data)) #np
        return new_data
        
# for GUI purposes: SPLIT MODULE HERE
def kmeans(new_data):
        # use elbow method to determine appropriate k value (number of clusters)
        distortions = []
        K = range(1,10)
        for k in K:
            kmeanModel = KMeans(n_clusters=k).fit(new_data)
            kmeanModel.fit(new_data)
            distortions.append(sum(np.min(cdist(new_data,kmeanModel.cluster_centers_,'euclidean'),axis=1)))

        plt.plot(K, distortions, 'bo-')
        plt.xlabel('Possible K values')
        plt.ylabel('Distortion')
        plt.title("Finding Optimal K via Elbow Method")

def cluster(k,new_data):
        #plt.show()
    
        #k = int(input("Based on the visual representation of the elbow method, enter number of clusters: "))
    
        # apply k-means on this normalized data
        kmeans = KMeans(init='k-means++',n_clusters=k,n_init=10)
        kmeans.fit(new_data)
        #numpy new_data
        y_kmeans = kmeans.predict(new_data)
        plt.scatter(new_data[:,0], new_data[:,1], c=y_kmeans,s=50,cmap='viridis')
        centroids = kmeans.cluster_centers_
        plt.scatter(centroids[:,0],centroids[:,1],c='black',s=200,alpha=0.5)
        #plt.show()
        # cluster data = [[<data point name>, <cluster label>].....]
        



################## END ########################

