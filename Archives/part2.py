"""
Program Title: ScanSphere - Part 2
Program Desc.: This program implements the specifications of Senior Design (SD) Part 2, which sorts the database 
entries and sorting them to create nodes and edges for graph construction in Part 3.
Authors: Dhivahari Vivek, Turgerel Amgalanbaatar, Hosna Zulali, Kulprawee Prayoonsuk, Katerina Walter
"""
import os
import sys
import json
import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def createAttr(attr,value,myATT,myNODES):
    print("creating attribute collection documemt...")
    print("Attr:", attr, "value:", value)
    # creating new attribute document
    attDoc = { "att_key": attr, "att_val": value }
    a = myATT.insert_one(attDoc)
    # create a node doc of type (A)ttribute
    print("connecting attribute coll to node type A...")
    nodeDoc = {"node_type": "A", "ref_ID": a.inserted_id }
    print("done creating att node")
    b = myNODES.insert_one(nodeDoc)
    print("done inserting att node")
    return b

def compareAll(attr,value,myATTdoc):
    
    if type(attr) == type (myATTdoc["att_key"]):
        #do normal check
        if attr == myATTdoc["att_key"]:
            if type(value) == type(myATTdoc["att_val"]):
                #do normal check
                if value == myATTdoc["att_val"]:
                    return True #iff all match
                else:
                    return False
                
            else:
                print("Fix type compare 1")
                #fix type compare
        else:
            return False
    else:
        print("Fix type compare 2")
        #fix type compare
    
    return False

# will change edge weight appropriately (1 for now)
def edgeWeight():
    return 1

def createEdge(src,des):
    print()
    print("creating new edge")
    weight = edgeWeight()
    edgeDoc = {'node1': src, 'node2':des, 'weight': weight}
    return edgeDoc

# connecting to database / appropriate collections
def populateHostNode():
    try:
        # establishing connection
        print("Connecting to database...")
        myClient = MongoClient("mongodb+srv://dbAdmin:dbAdmin123@scandata-fjmex.mongodb.net/test?retryWrites=true&w=majority")
        myDB = myClient.ScanData	# accesses database
        
        myNMAP = myDB.nmapData          # accesses raw data (nmapData collection)
        myNODES = myDB.nodes		# accesses nodes (nodes collection)
        myATT = myDB.attributes         # accesses attributes (attributes collection)
        myEDGES = myDB.edges		# accesses edges (edges collection)
        
        myNODES.drop()  # clearing host nodes each run (for new scan)
        myATT.drop()    # clearing attribute docs
        myEDGES.drop()  # clearing edges doc 

        print ("creating host nodes...")
        # iterating through nmapList collection (raw data)
        for x in myNMAP.find():
            myDoc = { "node_type": "H", "ref_ID": x['_id'] }   # creating Nodes doc of type (H)ost
            y = myNODES.insert_one(myDoc)       # inserting this document into Nodes Collection

        # iterating through host nodes in node collection
        for x in myNODES.find({"node_type":"H"}):
            # print("NODES doc: " , x, '\n')
            myQuery = { "_id": x['ref_ID']}     # accessing nmapData via host node's reference ID
            myNMAPdoc = myNMAP.find_one(myQuery)   # temporarily saving the NMAP doc in question 
            scanData = myNMAPdoc.get("scanData")    # retrieving attributes from each nmap node
            # for each pair of attributes
            print()
            print("checking for attribute values...")
            dest = '' #object id 
            for attr, value in scanData.items():   #attr,value of nmapData for each H type node
                # for each Node document of type (A)ttribute 
                # compare against existing nodes for this exact combo
                results = myNODES.find({"node_type":"A"})
                print()
                print("searching through node type A results....len:", myNODES.count_documents({"node_type":"A"}))
                counter = 0
                isFound = False
                for res in results:
                    counter+=1
                    nodeQuery = {"_id": res["ref_ID"]}    # accessing attribute doc via att node's reference ID
                    myATTdoc = myATT.find_one(nodeQuery)   # temporarily saving the ATTR doc in question
                    
                    if compareAll(attr,value,myATTdoc): #if T.E. A type node with attr,value, no action needed
                        print("Compare True")
                        dest = res['_id']
                        isFound = True
                        break
                if not isFound:
                    print("creating new A type node")
                    result = createAttr(attr,value,myATT,myNODES)
                    dest = result.inserted_id
                    print(result, attr, value) #print resulting A type node
                    
                # making edges
                print(type(x['_id']))
                print("making edge")
                newEdge = createEdge(x['_id'],dest)
                print(type(newEdge),newEdge)
                edgeResult = myEDGES.insert_one(newEdge)
                print()
                print(edgeResult)
            
                    
               
    except Exception as e:
      print(e)


def main():
    try: 
        # populating nodes of type (H)ost
        populateHostNode()
    except Exception as e:
        print(e)

#END MAIN

main()
