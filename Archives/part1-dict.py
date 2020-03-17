"""
Program Title: ScanSphere - Part 1 (dictionary)
Program Desc.: This program implements the specifications of Part 1 using a dictionary, which parses nmap results
(Dhivahari, Turgerel, Hosna) and prepares them for database transfer (Katerina, Kulprawee). This is an earlier
draft of ScanSphere - Part 1.
Authors: Dhivahari Vivek, Turgerel Amgalanbaatar, Hosna Zulali, Kulprawee Prayoonsuk, Katerina Walter
"""
import os
import sys
import nmap
import json
import networkx as nx
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# use to output a local json file instead of sending to main db
def makeJson(nm):
    # creating list of nmap dictionaries
    nmapList = []
    for count in nm.all_hosts():
        nmapOBJ = {}    # creating empty dictionary for each host
        # data must be parsed differently depending on whether OS info can be collected
        # TODO: as info list expands, change to (IF NULL DONT ADD KEYVALUE PAIR)
        nmapOBJ['host_IP']=count
        nmapOBJ['host_name']=nm[count].hostname()
        nmapOBJ['host_state']=nm[count].state()
        nmapOBJ['all_protocols']=nm[count].all_protocols()
        nmapOBJ['tcp_opens']=nm[count].all_tcp()
        nmapOBJ['udp_open']=nm[count].all_udp()
        nmapOBJ['ip_open']=nm[count].all_ip()
        nmapOBJ['sctp_open']=nm[count].all_sctp()
        if 'osmatch' in nm[count]:
            for osmatch in nm[count]['osmatch']:
                nmapOBJ['os_type']=osmatch['osclass'][0]['type']
                nmapOBJ['os_vend']=osmatch['osclass'][0]['vendor']
                nmapOBJ['os_fam']=osmatch['osclass'][0]['osfamily']
                nmapOBJ['os_gen']=osmatch['osclass'][0]['osgen']
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
# END DEF makejson

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
# end mainmenu

def parseScanDoc(nm,count):
    nmapOBJ = {}    # creating empty dictionary for each host
    # data must be parsed differently depending on whether OS info can be collected
    # TODO: as info list expands, change to (IF NULL DONT ADD KEYVALUE PAIR)
    # nmapOBJ['host_IP']=count
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

    return nmapOBJ
# end parseScan

def mainScan(ip):
    nm = nmap.PortScanner()

    # running scans based on IP addresses user entered
    nm.scan(ip, '0-443', arguments='-O')

    # creating list of DOCUMENTS
    print("Consolidating data...")
    nmapList = []
    for count in nm.all_hosts():
        nmapOBJ = parseScanDoc(nm,count)
        mach_doc = {'hostIP' : count, 'scanData' : nmapOBJ}
        nmapList.append(mach_doc)
    return nmapList
# end mainScan

def rawtoDB(nmapList):
    try:
        # ***Send to DB***#
        print("Connecting to database...")
        myclient = MongoClient("mongodb+srv://dbAdmin:dbAdmin123@scandata-fjmex.mongodb.net/test?retryWrites=true&w=majority")
        mydb=myclient.ScanData # database
        mycol = mydb.nmapData # collection
        print("Sending to database...")
        results = mycol.insert_many(nmapList)
        # result = mycol.insert_one(nmapList[0])
        return results
    except Exception as e:
        print(e)
# end rawtoDB



###################################################################

def main():

    try:
        ip = mainmenu() # get ip(s) to scan
        nmapList = mainScan(ip) # nmapList is list of Documents (hostIP, Values<dict>) to import
        results = rawtoDB(nmapList) # send scanned data to DB
        
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
        
        # for all successful IDs inserted to db, add objectID string to graph G
        for element in results.inserted_ids:
            G.add_node(element)
        print(G.nodes())
        print(G.edges())

        print(type(G.nodes()))
        print(type(G.edges()))
            

    except Exception as e:
        print(e)
# END MAIN

main()
