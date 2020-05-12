# ScanSphere
**ABOUT**

Network scanners and vulnerability analysis tools are invaluable in discovering fingerprinting data about network hosts. These fingerprints consists of a diverse and large variety of attributes, ranging from host OS and open or closed ports, to running services and their patch levels or vulnerabilities.

Similarity of these fingerprints can provide very important insights for network security administrators for tackling threat propagation, or conducting forensics analysis. For example, if a system with fingerprint A is infected with a malware, hosts with fingerprints similar to A are the most immediate candidate machines that need to be investigated for possible infection. Our goal in this project is to develop ScanSphere, a network mapper tool that uses off-the-shelf scanning tools to fingerprint hosts in a network or across various networks, and then clusters these hosts based on the similarity of their whole or partial fingerprints. In other words, our tool generates a high-level map of the network where hosts are clustered according to their fingerprint similarity. In order to tackle the curse of dimensionality, our approach uses network embedding techniques. This tool provides network administrators with a holistic view of the network, and assists them in real-time security decisions regarding threat management and analytics.

ScanSphere was designed, implemented, and debugged/troubleshot by Dhivahari Vivek, Turgerel Amgalanbaatar, Hosna Zulali, Katerina Walter, and Kulprawee Prayoonsuk. This tool was developed as part of a senior design research project under the direction of Dr. Haadi Jafarian and Masoumeh Abolfathi over two semesters at the University of Colorado Denver.

<details>
  <summary>SEMESTER 1: Network Scanning, Graph Construction, and Graph Embedding</summary> 

#### Part 1 - Nmap Network Scan
The tool gives the user three scanning options: scan a single IP address, scan a range of IP addresses, or scan several specific IP addresses. It uses Nmap (more specifically, the *python-nmap* library that helps in using the Nmap port scanner) and then prepares the raw nmap data for database transfer.

#### Part 2 - Database Collection, Graph Node/Edge Generation
The tool transfers the raw Nmap data collected in Part 1 to a MongoDB server which will store the scanned network's data. The data is then sorted into nodes (hosts and attributes) and edges (relationships between hosts and attributes) for graph construction in Part 3. See the ScanSphere/graph-construction.md to understand this process in further detail.

#### Part 3 - Graph Construction
The nodes and edges generated in Part 2 will be used to construct a directed, weighted graph (using Python's *NetworkX* library). 

#### Part 4 - Graph Embedding Methods (GEM)
The tool will then execute the Structured Deep Network Embedding (SDNE) and node2vec graph embedding techniques (using the *GEM* library).

</details>

<details>
  <summary>SEMESTER 2: Graphical User Interface (GUI), Clustering Methods</summary>
  
  #### Part 1 - K-Means Clustering 
  The tool uses K-Means clustering to cluster the hosts according to fingerprint similarity, and employs the Elbow Method to calculate the optimal k value (or the optimal number of clusters).
  
  #### Part 2 - GUI
  The tool's Graphic User Interface (GUI) is built using Python's tkinter library.

</details>
