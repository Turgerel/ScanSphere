# Graph Construction

Part 2 of the tool's implementation sorts the raw Nmap data in the MongoDB database into nodes and edges. This implementation required a very extensive process in order to properly reference MongoDB documents, to create separate "host" and "attribute" nodes, and to account for every attribute_key/value saved (for instance, if the attribute/key combination was already found in a previous host, then the attribute node for that key/value need not be created again).

The design for the algorithm written in Part 2 is written below, with the names of the appropriate MongoDB collections.

1. **Execute the nmap scans as already implemented and populate the database's nmapData Collection (in other words, the raw nmap scan data).**
    a.) The Node collection, the Edge collection, and the Attribute collection in the ScanData database. 
    b.) These four collections generate a document per entry, and each document has its own automatically generated Object ID.
