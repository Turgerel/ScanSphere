# Graph Construction

Part 2 of the tool's implementation sorts the raw Nmap data in the MongoDB database into nodes and edges. This implementation required a very extensive process in order to properly reference MongoDB documents, to create separate "host" and "attribute" nodes, and to account for every attribute_key/value saved (for instance, if the attribute/key combination was already found in a previous host, then the attribute node for that key/value need not be created again).

The design for the algorithm written in Part 2 is written below, with the names of the four appropriate MongoDB collections:
    - *nmapData*: contains the raw nmap data
    - *nodes*: contains either host nodes (type: "H") or attribute nodes (type: "A")
    - *attributes*: contains each attribute_key/value pair collected in a network scan (i.e. os_vendor/"Microsoft")
    - *edges*: contains each edge in a graph that connects the host node and the attribute node and the appropriate weight

Additionally, the database contains a fifth collection called *counter* which assigns each node a numerical ID suitable for graph construction and graph embedding.

1. **Execute the nmap scans as already implemented and populate the database's nmapData Collection (in other words, the raw nmap scan data).**
    - Each collection generates a document per entry, and each document has its own MongoDB-assigned object ID.

2. **Populate Nodes Collection with type (H)ost**
    - Parse through nmapData collection by document.
        - For each nmapData document (in other words, for each host scanned), a node document (for the *nodes* collection) is created.
        - This node document automatically generates an object ID and has a reference ID to the nmapData document it came from.
        - In the node document, assign a node type (H)ost or (A)ttribute.
    - By the end of this step, all node documents of type "(H)ost" should be created for every host scanned.

3. **Populate Node Collection with type (A)ttribute and Edges collection.**
    - For every "(H)ost"-type node collection document (created in step 2)...
        - Take the reference ID of the document to find the corresponding nmapData document and iterate through the host's attributes.
        - For every attribute_key/value (i.e. os_name/"Ubuntu") found in this nmapData document...
            - Search the node collection document of type (A)ttribute using the reference ID to the attribute collection document.
                - **IF MATCH FOUND** (in other words, if after looking through the nodes document, we find one whose reference ID                           matches the object ID of the corresponding Attributes document): Make an edge between node collection document of                       type (H)ost and node collection document of type (A)ttribute.
                - **IF MATCH NOT FOUND** (in other words, if the key/combo do not exist together): Look through the entire nodes                           collection at this point and check if any of them are of type (A)ttribute. Attempt to find a node document of type                     (A)ttribute with a reference ID that connects to the appropriate Attributes collection document).
                
