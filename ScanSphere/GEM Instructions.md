# INSTRUCTIONS TO DOWNLAOD AND RUN GEM

Our ScanShpere tool utilizes the GEM library, specifically **node2vec** and **SDNE**. 
Here are the instructions to download GEM and running the particular graph embedding techniques.

**DOWNLOAD GEM**

    1. Download GEM: https://github.com/palash1992/GEM
    
    2. Go into the *tests* folder
    
    3. Open the *test_karate.py* python file
    
    4. Comment outlines 13 - 16 so that you only have: 
                from gem.embedding.node2vec import node2vec
                from gem.embedding.sdne     import SDNE
