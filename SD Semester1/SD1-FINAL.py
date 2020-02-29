"""
Program Title: SD-final
Program Desc.:
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

#use to output a local json file instead of sending to main db
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
    for node in nmapList: #nmapList list of 'machine' dictionaries. machine dictionary key-ip address, value dictionary of values
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
#end mainmenu

def parseScanDoc(nm,count):
##IF UPDATED, json function will not match. Make appropriate changes##
    nmapOBJ = {}    # creating empty dictionary for each host
    # data must be parsed differently depending on whether OS info can be collected
    #TODO: as info list expands, change to (IF NULL DONT ADD KEYVALUE PAIR)
    #nm type = <class 'nmap.nmap.PortScanner'>
    #nm[count] type = <class 'nmap.nmap.PortScannerHostDict'>
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
#end parseScan

def customScan(var1, var2):
#TODO: customize the nmap scan run
    return var1,var2

def mainScan(ip):
    print ("Scanning...")
    nm = nmap.PortScanner()
    scanDatetime = datetime.datetime.now()
    # running scans based on IP addresses user entered
    #customScan() #set appropriate arguments, range for scan
    nm.scan(ip, '0-443', arguments='-O')
    #nm.scan(ip,var1,var2)
    # creating list of DOCUMENTS
    print("Consolidating data...")
    nmapList = []
    for count in nm.all_hosts():
        nmapOBJ = parseScanDoc(nm,count)
        mach_doc = {'scanID': scanDatetime, 'hostIP' : count, 'scanData' : nmapOBJ}
        nmapList.append(mach_doc)
    return nmapList
#end mainScan

def rawtoDB(nmapList):
    try:
        #***Send to DB***#
        print("Connecting to database...")
        myclient = MongoClient("mongodb+srv://dbAdmin:dbAdmin123@scandata-fjmex.mongodb.net/test?retryWrites=true&w=majority")
        mydb=myclient.ScanData #database
        mycol = mydb.nmapData #collection
        print("Sending to database...")
        results = mycol.insert_many(nmapList)
        #result = mycol.insert_one(nmapList[0])
        return results
    except Exception as e:
        print(e)
#end rawtoDB

def incrementCounter(myCounter):
    x = myCounter.find_one()    # found the counter
    temp = x['counter']
    temp += 1        # increment counter - which is the index of the node
    x1 = { "$set": { "counter" : temp}}
    new_x = myCounter.update_one(x,x1)     # update
    return 0

def createAttr(attr,value,myATT,myNODES, myCounter):
    print("creating attribute collection documemt...")
    print("Attr:", attr, "value:", value)
    # creating new attribute document
    attDoc = { "att_key": attr, "att_val": value }
    a = myATT.insert_one(attDoc)
    # create a node doc of type (A)ttribute
    print("connecting attribute coll to node type A...")
    #nodeDoc = {"node_type": "A", "ref_ID": a.inserted_id }
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    b = myCounter.find_one()
    nodeDoc = {'num_ID': b['counter'], "node_type": "A", "ref_ID": a.inserted_id}
    incrementCounter(myCounter)
    #nodeDoc = {"_id" : collection}
    
    print("done creating att node")
    c = myNODES.insert_one(nodeDoc)
    print("done inserting att node")
    return c

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
        myDB = myClient.ScanData    # accesses database
        
        myNMAP = myDB.nmapData          # accesses raw data (nmapData collection)
        myNODES = myDB.nodes        # accesses nodes (nodes collection)
        myATT = myDB.attributes         # accesses attributes (attributes collection)
        myEDGES = myDB.edges        # accesses edges (edges collection)
        myCounter = myDB.counter
            #for x myCounter.find(): x['counter']
          #5e35f6951c9d440000412c63['counter']
        
        myNODES.drop()  # clearing host nodes each run (for new scan)
        myNODES.create_index("num_ID")
        myATT.drop()    # clearing attribute docs
        myEDGES.drop()  # clearing edges doc

        print ("creating host nodes...")
        # iterating through nmapList collection (raw data)
        for x in myNMAP.find():
            #myDoc = { "node_type": "H", "ref_ID": x['_id'] }   # creating Nodes doc of type (H)ost
            #!!!!!!!!!!!!!!!!!!!!!!!!
            #a = myCounter.find_one({"_id":"5e35f6951c9d440000412c63"})
            a = myCounter.find_one()
            a_val = a['counter']
            myDoc = {'num_ID': a_val, "node_type": "H", "ref_ID": x['_id'] }
            print(myDoc)

            incrementCounter(myCounter)

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
                    result = createAttr(attr,value,myATT,myNODES,myCounter)
                    dest = result.inserted_id
                    print(result, attr, value) #print resulting A type node
                    
                # making edges
                print(type(x['_id']))
                print("making edge")
                b = myNODES.find_one({"_id":dest})
                newEdge = createEdge(x['num_ID'],b['num_ID'])
                #TODO CHANGE TO ENUMERATION CODES INSTEAD
                print(type(newEdge),newEdge)
                edgeResult = myEDGES.insert_one(newEdge)
                print()
                print(edgeResult)
            
                    
               
    except Exception as e:
      print(e)


###################################################################

def main():

    try:
        ip = mainmenu() #get ip(s) to scan
        nmapList = mainScan(ip) #nmapList is list of Documents (hostIP, Values<dict>) to import
        results = rawtoDB(nmapList) #send scanned data to DB
        
    except Exception as e:
        print(e)

    try:
        # populating nodes of type (H)ost
        populateHostNode()
    except Exception as e:
        print(e)

#END MAIN

main()


"""----------GRAPH CONSTRUCTION----------"""
# DiGraph is a base class for directed graphs (stores directed edges)
G = nx.DiGraph()

# establishing connection
print("Connecting to database...")

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
    G.add_edge(host_node, att_node, weight = w)

# for DEMO --> printing each edge's end nodes and weight
for u, v, weight in G.edges(data='weight'):
    if weight is not None:
        print(u,v)
        

print("\nThe total number of nodes is: ", G.number_of_nodes(),'\n')
