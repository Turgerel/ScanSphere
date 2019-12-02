"""
Program Title: SD1-P1
Program Desc.: This program implements the specifications of Senior Design (SD) Part 1, which parses nmap results
(Dhivahari, Turgerel, Hosna) and prepares them for database transfer (Katerina, Kulprawee).
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

def compareAll():
    #TODO implement comparison between types
    return True

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
            print("checking for attribute values...")
            for attr, value in scanData.items():
                # for each Node document of type (A)ttribute 
                # compare against existing nodes for this exact combo
                results = myNODES.find({"node_type":"A"})
                isFound = False
                for res in results:
                    print("searching through node type A results....")
                    nodeQuery = {"_id": res["ref_ID"]}    # accessing attribute doc via att node's reference ID
                    myATTdoc = myATT.find_one(nodeQuery)   # temporarily saving the ATTR doc in question
                    print(myATTdoc, type(myATTdoc))
                    # if the combination already exists as an attribute node
                    print(type(myATTdoc["att_key"]), type(attr))
                    print(type(myATTdoc["att_val"]), type(value))
                    #TODO implement comparison fuction, replace this line below!
                    if myATTdoc["att_key"] == attr and myATTdoc["att_val"] == value:
                        isFound = True
                if not isFound:
                    result = createAttr(attr,value,myATT,myNODES)
                    print(result)
                    
               
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
