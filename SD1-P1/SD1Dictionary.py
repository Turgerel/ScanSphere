"""
Program Title: SD1-P1
Program Desc.: This program implements the specifications of Senior Design (SD) Part 1, which parses nmap results 
(Dhivahari, Turgerel, Hosna) and prepares them for database transfer (Katerina, Kulprawee).
Authors: Turgerel Amgalanbaatar, Hosna Zulali, Dhivahari Vivekanandasarma, Kulprawee Prayoonsuk, Katerina Walter
"""
import os
import sys
import nmap
import json

try:
    menu = int(input("\nMake a selection:\n1. Scan a single IP address.\n2. CURRENTLY UNAVAILABLE - Scan a range of IP addresses.\n3. Scan different IP addresses.\n\n"))
    # scanning single IP
    if(menu == 1):
        nm = nmap.PortScanner()
        ip = input("\nEnter the IP to be scanned: ")
        print("scanning single IP address...")
        # BELOW, THE SCANS CONDUCTED
        nm.scan(ip, '21-443')   # port scanning user-entered IP from ports 21-443
        nm.scan(ip, arguments='-O')     # OS detection using TCP/IP stack fingerprinting
    # scanning a range of IP
    elif(menu == 2):
        nm = nmap.PortScannerAsync()
        # this function is needed for async scanning
        def callback_result(host, scan_result):
            print('-------------------------------')
            print(host, scan_result)
        ip = input("\nEnter the range of IP addresses (example: 192.168.1.0/30): ")
        print("scanning given range of IP addresses...")
        nm.scan(ip,'21-443')
        nm.scan(ip, arguments='-O', callback=callback_result)
    # scanning different IPs
    elif(menu == 3):
        nm = nmap.PortScanner()
        ip = input("\nEnter the IP addresses to be scanned (EACH SEPARATED BY A SINGLE SPACE): ")
        print("scanning entered IP addresses...")
        # BELOW, THE SCANS CONDUCTED
        nm.scan(ip, '21-443')   
        nm.scan(ip, arguments='-O')

    # creating list of nmap dictionaries
    nmapList = []
    index = 0
    for count in nm.all_hosts():
        nmapOBJ = {}    # creating an empty dictionary for each host
        nmapOBJ = {'host_name':nm[count].hostname(),
                'host_state':nm[count].state(),
                'os_accuracy':"",
                'os_family':"",
                'os_generation':""
                }
        nmapList.append(nmapOBJ)
        index+=1
        
    index = 0
    if 'osclass' in nm[ip]:
        for osclass in nm[ip]['osclass']:
            nmapList[index]['os_accuracy'] = osclass['accuracy']
            nmapList[index]['os_family'] = osclass['osfamily']
            nmapList[index]['os_generation'] = osclass['osgen']

    
    # preparing for JSON extraction
    machine = {}
    # iterating through nmapList to convert each node's data to JSON
    index = 0
    for node in nmapList:
        machine[nmapList[index]['host_name']]={
                'host_state': nmapList[index]['host_state'],
                'os_accuracy': nmapList[index]['os_accuracy'],
                'os_family': nmapList[index]['os_family'],
                'os_generation': nmapList[index]['os_generation']
                }

    s = json.dumps(machine)
    
    # formally creating json file to be used for database entry
    with open("nmap_nodes.json","w") as f:
      f.write(s)

except Exception as e: 
  print(e)
