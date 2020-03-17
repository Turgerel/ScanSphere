"""
Program Title: ScanSphere - Part 1
Program Desc.: This program implements the specifications of Senior Design (SD) Part 1, which parses nmap results 
(Dhivahari, Turgerel, Hosna) and prepares them for database transfer (Katerina, Kulprawee).
Authors: Turgerel Amgalanbaatar, Hosna Zulali, Dhivahari Vivekanandasarma, Kulprawee Prayoonsuk, Katerina Walter
"""
import os
import sys
import nmap
import json

try:
    nm = nmap.PortScanner() # creating object that will hold our scan
    # scan options menu HERE
    menu = int(input("\nMake a selection:\n1. Scan a single IP\n2. Scan a range\n\n"))
    # scanning single IP
    if(menu == 1):
        ip = input("\nEnter the IP to be scanned: ")
        print("scanning single IP")
    # scanning multiple IPs
    elif(menu == 2):
        print("scanning range")
    # BELOW, THE SCANS CONDUCTED
    nm.scan(ip, '21-443')   # port scanning user-entered IP from ports 21-443
    nm.scan(ip,arguments='-O')  # OS detection using TCP/IP stack fingerprinting

    # nmap object class (instances of these class will be each host scanned)
    class nmapOBJ(object): 
        def __init__(self,host_IP,host_name,host_state,OSacc,OSfam,OSgen):
            self.host_IP = host_IP
            self.host_name = host_name
            self.host_state = host_state
            self.OSacc = OSacc
            self.OSfam = OSfam
            self.OSgen = OSgen

    # creating list of nmapOBJ of size total number of hosts found in scan
    nmapList = []
    for count in nm.all_hosts():
        hIP = "to be determined"
        hName = "to be determined"
        hState = "to be determined"
        accOS = "to be determined"
        famOS = "to be determined"
        genOS = "to be determined"
        nOBJ = nmapOBJ(hIP,hName,hState,accOS,famOS,genOS)
        nmapList.append(nOBJ)
	
        """
	NOTE: It seems we have to parse different categories of data independently. For example, 
	HOST/PORT information can be parsed through the PortScanner() function, but OS info
	has to be extracted from the "osclass" for each IP address scanned. So...below:
	"""
    # parsing data to list of nmapOBJ for PORT information
    index = 0
    for host in nm.all_hosts():
        nmapList[index].host_name = nm[host].hostname()
        nmapList[index].host_state = nm[host].state()

    index = 0
    # parsing data to list of nmapOBJ for OS information
    if 'osclass' in nm[ip]:
        for osclass in nm[ip]['osclass']:
            nmapList[index].OSacc = osclass['accuracy']
            nmapList[index].OSfam = osclass['osfamily']
            nmapList[index].OSgen = osclass['osgen']
            index+=1

    # just printed the details of the first machine object to see if all the data went in
    print("\n------------------------------------")
    print("NMAP SCAN DETAILS (Machine 01)\n------------------------------------\n")
    print("HOST DETAILS\n.......................\n")
    print("Host name: ", nmapList[0].host_name)
    print("Host state: ", nmapList[0].host_state)
    print("\nOS DETAILS\n.........................\n")	
    print("OS accuracy: ", nmapList[0].OSacc)
    print("OS family: ", nmapList[0].OSfam)
    print("OS generation: ", nmapList[0].OSgen)
    print("\n")
    
    # preparing for JSON extraction
    machine = {}
    # iterating through nmapList to convert each node's data to JSON
    index = 0
    for node in nmapList:
        machine[nmapList[index].host_name]={
                'host_state': nmapList[index].host_state,
                'os_accuracy': nmapList[index].OSacc,
                'os_family': nmapList[index].OSfam,
                'os_generation': nmapList[index].OSgen
                }

    s = json.dumps(machine)
    
    # formally creating json file to be used for database entry
    with open("nmap_nodes.json","w") as f:
      f.write(s)

except Exception as e: 
  print(e)
