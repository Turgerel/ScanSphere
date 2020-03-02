# SD project "network mapper"
**ABOUT**

Network scanners and vulnerability analysis tools are invaluable in discovering fingerprinting data about network hosts. These fingerprints consists of a diverse and large variety of attributes, ranging from host OS and open or closed ports, to running services and their patch levels or vulnerabilities.

Similarity of these fingerprints can provide very important insights for network security administrators for tackling threat propagation, or conducting forensics analysis. For example, if a system with fingerprint A is infected with a malware, hosts with fingerprints similar to A are the most immediate candidate machines that need to be investigated for possible infection. Our goal in this project is to develop a network mapper tool that uses off-the-shelf scanning tools to fingerprint hosts in a network or across various networks, and then clusters these hosts based on the similarity of their whole or partial fingerprints. In other words, our tool generates a high-level map of the network where hosts are clustered according to their fingerprint similarity. In order to tackle the curse of dimensionality, our approach uses network embedding techniques. This tool provides network administrators with a holistic view of the network, and assists them in real-time security decisions regarding threat management and analytics.

<details>
  <summary>SEMESTER 1: Senior Design CSCI 4738</summary> 

#### SD1-P1.py
Our first goal was making a network scanner using NMAP python library, parsing the results, and creating a JSON file with the collected network information in order for it to be used in our database.

#### SD1-P2.py
Our second goal was using our raw network data to sort and create entries, nodes, and edges for the graph construction. Here is a link to our thought process of the graph construction. (Note: Relationship entity model) 

https://docs.google.com/document/d/1hECHP02wrSGvhkiV0S3u3GbYJ4b4J8GDqd7kqQ7VGAA/edit?usp=sharing

#### SD1-P3.py
Our third goal was to actually construct the graph using our EDGES collection from our database. The graph is very crucial since it will be used in the graph embedding functions/techniques through the GEM Library. We are mostly using SDNE and node2vec. 

Here is a link to the GEM Library repo.

https://github.com/palash1992/GEM
</details>

<details>
  <summary>SEMESTER 2: Senior Design CSCI 4739</summary>
  
#### SD2-P1.py
Our current goal is to create a GUI(with visualizations) for our tool while providing information about the scanned network.
</details>
