"""
Program Title: SD1-P1
Program Desc.: This program implements the specifications of Senior Design (SD) Part 1, which parses nmap results 
(Dhivahari, Turgerel, Hosna) and prepares them for database transfer (Katerina, Kulprawee).
Authors: Turgerel Amgalanbaatar, Hosna Zulali, Dhivahari Vivekanandasarma, Kulprawee Prayoonsuk, Katerina Walter
"""
import os
import sys
import nmap

nm = nmap.PortScanner() # creating object that will hold our scan
ip = input("\nEnter the IP to be scanned: ") # asking user to enter IP to be scanned

# BELOW, THE SCANS CONDUCTED
nm.scan(ip, '21-443')   # port scanning user-entered IP from ports 21-443
nm.scan(ip,arguments='-O')  # OS detection using TCP/IP stack fingerprinting

"""
I FEEL LIKE THERE IS A MORE ORGANIZED WAY TO ORGANIZE HOST DATA, PORT DATA,
OS DATA, etc. Right now it's just all a jumble of attributes in here, and
I haven't found time to properly look at good ways to organize them within the 
class nmapOBJ...so maybe once we really get it to work we can think about or-
ganizing them?
ok
"""

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

index = 0
# parsing data to list of nmapOBJ for PORT information
for host in nm.all_hosts():
    nmapList[index].host_name = nm[host].hostname()
    nmapList[index].host_state = nm[host].state()
    index+=1

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




