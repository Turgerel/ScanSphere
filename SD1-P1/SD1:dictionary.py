{\rtf1\ansi\ansicpg1252\cocoartf1671\cocoasubrtf600
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 """\
Program Title: SD1-P1\
Program Desc.: This program implements the specifications of Senior Design (SD) Part 1, which parses nmap results \
(Dhivahari, Turgerel, Hosna) and prepares them for database transfer (Katerina, Kulprawee).\
Authors: Turgerel Amgalanbaatar, Hosna Zulali, Dhivahari Vivekanandasarma, Kulprawee Prayoonsuk, Katerina Walter\
"""\
import os\
import sys\
import nmap\
import json\
\
try:\
    nm = nmap.PortScanner() # creating object that will hold our scan\
    # scan options menu HERE\
    menu = int(input("\\nMake a selection:\\n1. Scan a single IP\\n2. Scan a range\\n\\n"))\
    # scanning single IP\
    if(menu == 1):\
        ip = input("\\nEnter the IP to be scanned: ")\
        print("scanning single IP")\
    # scanning multiple IPs\
    elif(menu == 2):\
        print("scanning range")\
    # BELOW, THE SCANS CONDUCTED\
    nm.scan(ip, '21-443')   # port scanning user-entered IP from ports 21-443\
    nm.scan(ip,arguments='-O')  # OS detection using TCP/IP stack fingerprinting\
\
    # creating list of nmap dictionaries\
    nmapList = []\
    index = 0\
    for count in nm.all_hosts():\
        nmapOBJ = \{\}    # creating an empty dictionary for each host\
        nmapOBJ = \{'host_name':nm[count].hostname(),\
                'host_state':nm[count].state(),\
                'os_accuracy':"",\
                'os_family':"",\
                'os_generation':""\
                \}\
        nmapList.append(nmapOBJ)\
        index+=1\
        \
    index = 0\
    if 'osclass' in nm[ip]:\
        for osclass in nm[ip]['osclass']:\
            nmapList[index]['os_accuracy'] = osclass['accuracy']\
            nmapList[index]['os_family'] = osclass['osfamily']\
            nmapList[index]['os_generation'] = osclass['osgen']\
\
    \
    # preparing for JSON extraction\
    machine = \{\}\
    # iterating through nmapList to convert each node's data to JSON\
    index = 0\
    for node in nmapList:\
        machine[nmapList[index]['host_name']]=\{\
                'host_state': nmapList[index]['host_state'],\
                'os_accuracy': nmapList[index]['os_accuracy'],\
                'os_family': nmapList[index]['os_family'],\
                'os_generation': nmapList[index]['os_generation']\
                \}\
\
    s = json.dumps(machine)\
    \
    # formally creating json file to be used for database entry\
    with open("nmap_nodes.json","w") as f:\
      f.write(s)\
\
except Exception as e: \
  print(e)\
}