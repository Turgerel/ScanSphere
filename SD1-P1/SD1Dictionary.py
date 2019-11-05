"""
Program Title: SD1-P1
Program Desc.: This program implements the specifications of Senior Design (SD) Part 1, which parses nmap results
(Dhivahari, Turgerel, Hosna) and prepares them for database transfer (Katerina, Kulprawee).
Authors: Dhivahari Vivek, Turgerel Amgalanbaatar, Hosna Zulali, Kulprawee Prayoonsuk, Katerina Walter
"""
import os
import sys
import nmap
import json
import networkx as nx
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

try:
    menu = int(input("\nMake a selection:\n1. Scan a single IP address.\n2. Scan a range of IP addresses.\n3. Scan different IP addresses.\n\n"))

    nm = nmap.PortScanner()

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

    # running scans based on IP addresses user entered
    nm.scan(ip, '0-443', arguments='-O')

    # creating list of DOCUMENTS
    print("Consolidating data...")
    nmapList = []
    for count in nm.all_hosts():
    
        nmapOBJ = {}    # creating empty dictionary for each host
        # data must be parsed differently depending on whether OS info can be collected
        #TODO: as info list expands, change to (IF NULL DONT ADD KEYVALUE PAIR)
        #nmapOBJ['host_IP']=count
        nmapOBJ['host_name']=nm[count].hostname()
        nmapOBJ['host_state']=nm[count].state()
        nmapOBJ['all_protocols']=nm[count].all_protocols()
        nmapOBJ['tcp_open']=nm[count].all_tcp()
        nmapOBJ['udp_open']=nm[count].all_udp()
        nmapOBJ['ip_open']=nm[count].all_ip()
        nmapOBJ['sctp_open']=nm[count].all_sctp()
        if 'osmatch' in nm[count]:
            for osmatch in nm[count]['osmatch']:
                nmapOBJ['os_type']=osmatch['osclass'][0]['type']
                nmapOBJ['os_vend']=osmatch['osclass'][0]['vendor']
                nmapOBJ['os_fam']=osmatch['osclass'][0]['osfamily']
                nmapOBJ['os_gen']=osmatch['osclass'][0]['osgen']
        
        mach_doc = {'hostIP' : count, 'scanData' : nmapOBJ}
        
        nmapList.append(mach_doc)
        #END TODO SECTION
    
    #nmapList is list of Documents (hostIP, Values<dict>) to import
except Exception as e:
    print(e)

try:
    
    #***Send to DB***#
    print("Connecting to database...")
    myclient = MongoClient("mongodb+srv://dbAdmin:dbAdmin123@scandata-fjmex.mongodb.net/test?retryWrites=true&w=majority")
    mydb=myclient.ScanData #database
    mycol = mydb.nmapData #collection
    print("Sending to database...")
    results = mycol.insert_many(nmapList)
    #result = mycol.insert_one(nmapList[0])
    
except Exception as e:
    print(e)

  
try:
    
    G=nx.Graph()
    print(G.nodes())
    print(G.edges())

    print(type(G.nodes()))
    print(type(G.edges()))
    # adding just one node:
    G.add_node("a")
    # a list of nodes:
    G.add_nodes_from(["b","c"])
    
    #for all successful IDs inserted to db, add objectID string to graph G
    for element in results.inserted_ids:
        G.add_node(element)
    print(G.nodes())
    print(G.edges())

    print(type(G.nodes()))
    print(type(G.edges()))
        

except Exception as e:
    print(e)
