"""
Program Title: SD1-P2
Program Desc.: This program implements the graph construction of the network host and attribute nodes.
Authors: Dhivahari Vivek, Turgerel Amgalanbaatar, Hosna Zulali, Kulprawee Prayoonsuk, Katerina Walter
"""
import os
import sys
import json
import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


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

        # iterating through nmapList collection (raw data)
        for x in myNMAP.find():
            myDoc = { "node_type": "H", "ref_IP": x['hostIP'] }   # creating Nodes doc of type (H)ost
            y = myNODES.insert_one(myDoc)       # inserting this document into Nodes Collection

        # iterating through host nodes in node collection
        for x in myNODES.find():
            # print("NODES doc: " , x, '\n')
            myQuery = { "hostIP": x['ref_IP']}     # accessing nmapData via host node's reference ID
            myNMAPdoc = myNMAP.find(myQuery)   # temporarily saving the NMAP doc in question 
            for y in myNMAPdoc:
                print("NMAP temp doc:", y, '\n')
                

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
