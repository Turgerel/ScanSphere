# INSTRUCTIONS TO DOWNLAOD AND RUN GEM

Our ScanShpere tool utilizes the GEM library, specifically **node2vec** and **SDNE**. 
Here are the instructions to download GEM and running the graph embedding techniques.

**DOWNLOAD GEM**

1. Download GEM: https://github.com/palash1992/GEM
    
2. Go into the *tests* folder
    
3. Open the *test_karate.py* python file
    
4. Comment out lines 13 - 16 so that you only have: 

    *from gem.embedding.node2vec import node2vec*
    
    *from gem.embedding.sdne     import SDNE*
    
5. Comment out lines 33 - 36 so that you only have:

    *models.append(node2vec(d=2, max_iter=1, walk_len=80, num_walks=10, con_size=10, ret_p=1, inout_p=1))*
    
    *models.append(SDNE(d=2, beta=5, alpha=1e-5, nu1=1e-6, nu2=1e-6, K=3,n_units=[50, 15,], rho=0.3, n_iter=50,*                     xeta=0.01,n_batch=100,
                *modelfile=['enc_model.json', 'dec_model.json'],*
                *weightfile=['enc_weights.hdf5', 'dec_weights.hdf5']))*

6. Save the file

**SDNE (For all Operating Systems)**

Note: GEM WILL NOT BE ABLE TO WORK IF YOU HAVE ANACONDA INSTALLED.

1. On your terminal (cmd prompt, etc.) install specified versions:

    *pip3 install matplotlib==2.2.4*
    
    *pip3 install tensorflow==1.13.1*
    
2. Go to *tests* directory on your terminal and run the following:

    *python3 test_karate.py --SDNE 0*   
  
3. You should be able to see similar outputs as shown in the GEM GitHub Repository.

**NODE2VEC** 
#####sdf





