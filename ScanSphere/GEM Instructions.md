# INSTRUCTIONS TO DOWNLOAD AND RUN GEM

Our ScanSphere tool utilizes the GEM library, specifically **node2vec** and **SDNE**. 
Here are the instructions to download GEM and running the graph embedding techniques.

### Graph Embedding

We want to use graph embedding techniques to transform the constructed graph from our scanned network data in a new low dimensional space, where each node is represented as a vector.

### Structural Deep Network Embedding (SDNE)

SDNE is a graph embedding technique that tries to learn from the First-order proximity and the Second-order proximity instead of taking random walks. First-order proximity is when two nodes have a direct edge, hence we will consider them as neighbors. Second-order proximity is when two nodes have an indirect edge but are similar due to sharing multiple neighbors/adjacents nodes. The main purpose of SDNE is to capture highly non-linear structures by using the First-order(supervised) and Second-order(unsupervised) proximities which result in a semi-supervised network proximity. The reason for using SDNE for our ScanSphere tool is to make sure our graph was in a lower dimension, directed, and weighted. We wanted to have an algorithm that placed pentalties when similar nodes are mapped far from each other in the embedded space, thus permitting a zone for optimization through minimizing the space between those nodes. 

Here is the research paper discussing more on SDNE: https://www.kdd.org/kdd2016/papers/files/rfp0191-wangAemb.pdf


### Node2Vec 

Node2vec is a graph embedding technique that takes random walks, while investigating the neighboring nodes. Node2vec utilizes breadth-first-search(BFS) and depth-first-search(DFS) as parameters in order to decide what node it will be walking to next. Breadth-first-search is when the neighborhood is restricted to nodes that are immediate neighbors of the source; better for learning local neighbors. Depth-first-search is when the neighborhood consists of nodes sequentially sampled at increasing distances from the source node; better for learning global neighbors. Since these two are parameterized, node2vec can shift from one to the other depending on the task, hence displaying different results depending on the values of the parameters. We are using node2vec for the same reasons as that of SDNE as well as having a flexible algorithm that provides a diverse set of interpretations of the network neighborhood. 

Here is the research paper discussing more on node2vec: https://www.kdd.org/kdd2016/papers/files/rfp0218-groverA.pdf


<details>
    <summary>DOWNLOAD GEM</summary>

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
</details>

<details>
  <summary>SDNE (For all Operating Systems)</summary> 
<br>
**Note: GEM WILL NOT BE ABLE TO WORK IF YOU HAVE ANACONDA INSTALLED.**

1. On your terminal (cmd prompt, etc.) install specified versions:

    *pip3 install matplotlib==2.2.4*
    
    *pip3 install tensorflow==1.13.1*
    
2. Go to *tests* directory on your terminal and run the following:

    *python3 test_karate.py --SDNE 0*   
  
3. You should be able to see similar outputs as shown in the GEM GitHub Repository.

</details>

<details>
  <summary>NODE2VEC</summary> 


**FOR MAC OS**
1. Download Snap: https://github.com/snap-stanford/snap

2. Move your *snap-master* into the *GEM-master*

3. On your terminal, cd into your *snap-master* directory and run a *make all*
    
4. After *make all* is done, cd into *examples* and then cd into *node2vec* folder

5. Go into your bash file: *vi ~/.bash_profile* and change the export path:

    *export PATH=/Users/{user}/Desktop/SD/GEM-master/snap-master/examples/Release/:$PATH*
    
    ***Tip: You can go into the *examples* folder, drag and drop the *Release* folder into the bash file.***
    
6. In your *node2vec* folder, run: *./node2vec* to install

7. In your *node2vec* folder, run: *chmod +x ./node2vec* to give permission

8. Go back to the *tests* folder in *GEM-master* and run: 
    
    *python3 test_karate.py --node2vec 0* 

</details>


