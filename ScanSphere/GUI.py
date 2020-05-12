# import tkinter module 
from tkinter import *
import tkinter as tk
import tkinter.font as tkFont
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import scansphere as ss #from our own file, all the backend code for this project
import networkx as nx
import numpy as np


HEIGHT = 800
WIDTH = 900


# primary frame
root = tk.Tk()
root.title("ScanSphere")
canvas = tk.Canvas(root, bg='#374785',height=HEIGHT, width=WIDTH)
canvas.pack()

# -------------------title frame of GUI----------------------------
titleframe = tk.Frame(root,bg='#374785', bd=5)
titleframe.place(relx = 0.5, rely = 0.05, relwidth=0.75, relheight = 0.2, anchor='n')

titleFont = tkFont.Font(family="Times", size=75,weight=tkFont.BOLD)
title = tk.Label(titleframe,bg='#374785',fg="#CCCCCC",text="ScanSphere",font=titleFont)
title.place(relx = 0.5, rely = 0.3, anchor=CENTER)

label = tk.Label(titleframe,bg='#374785',fg="#CCCCCC",text="WARNING: Do not close this application while it's running!")
label.place(relx = 0.5, rely = 0.7, anchor = CENTER)


# -------------------scanning frame of GUI-------------------------
scanframe = tk.Frame(root, bg='#374785', bd=5)
scanframe.place(relx = 0.5, rely = 0.2, relwidth=0.75, relheight=0.2,anchor='n') 

# scan (1) single? (2) range? or (3) comma-separated IPs?
ipInputType = tk.IntVar()
ip1_button = tk.Radiobutton(scanframe,text="Single IP",bg='#374785',fg="#CCCCCC",variable=ipInputType, value=1,font=20)
ip1_button.place(relx = 0.25, rely = 0.25, anchor=CENTER)
ip2_button = tk.Radiobutton(scanframe,text="Range",bg='#374785',fg="#CCCCCC",variable=ipInputType,value=2,font=20)
ip2_button.place(relx = 0.5, rely = 0.25, anchor=CENTER)
ip3_button = tk.Radiobutton(scanframe,text="CS-IPs",bg='#374785',fg="#CCCCCC",variable=ipInputType, value=3,font=20)
ip3_button.place(relx = 0.75, rely = 0.25, anchor=CENTER)

enter_IP_font = tkFont.Font(family="Helvetica", size=15,weight=tkFont.BOLD)
# enter IP addresses and press the scan button
nmaplist = ""
entry = tk.Entry(scanframe, bg='#4E5F9C',fg='#CCCCCC', font=enter_IP_font)
entry.place(relx = 0.3335, rely = 0.8, relwidth=0.65,relheight=0.25, anchor=CENTER)
scanIP_button = tk.Button(scanframe, bg='#A895CC', text="Scan IP address(es)",command=lambda:ss.init_scan(nmaplist,entry), font=220)
scanIP_button.place(relx = 0.85, rely = 0.8, relheight = 0.25,relwidth = 0.3, anchor=CENTER)


# --------------------GEM+clustering frame of GUI----------------------
lower_frame = tk.Frame(root, bg = '#374785', bd = 10)
lower_frame.place(relx = 0.5, rely = 0.4, relwidth = 0.75, relheight = 0.45, anchor = 'n')

bodyFont = tkFont.Font(family="Times", size=25)

# create graph after the scan
G = nx.DiGraph()
graph_button = tk.Button(lower_frame, bg='#79B5A8', command=lambda: ss.build_graph(G))
graph_button.place(relx = 0.8, rely = 0.1, relwidth=0.1,relheight=0.125, anchor=CENTER)
graph_label = tk.Label(lower_frame, text="Build Graph", bg='#374785', fg="#CCCCCC", font=bodyFont)
graph_label.place(relx = 0.15, rely = 0.1, anchor=W)
# creates edge list
models = []
edgelist_button = tk.Button(lower_frame, bg='#79B5A8', command=lambda: ss.write_edges(G))
edgelist_button.place(relx = 0.8, rely = 0.3, relwidth=0.1, relheight=0.125, anchor=CENTER)
edgelist_label = tk.Label(lower_frame, text="Construct Edgelist", bg='#374785', fg="#CCCCCC", font=bodyFont)
edgelist_label.place(relx = 0.15, rely = 0.3, anchor=W)
# constructs GEM graph
GEM_button = tk.Button(lower_frame, bg='#79B5A8', command=lambda: ss.load_graph(G,models))
GEM_button.place(relx = 0.8, rely = 0.5, relwidth=0.1, relheight=0.125, anchor=CENTER)
GEM_label = tk.Label(lower_frame, text="Train GEM Graph",bg='#374785', fg="#CCCCCC", font=bodyFont)
GEM_label.place(relx = 0.15, rely = 0.5, anchor=W)
# constructs ELBOW graph
new_data = []
ELBOW_button = tk.Button(lower_frame, bg='#79B5A8', command=lambda: ss.build_elbow(models,new_data))
ELBOW_button.place(relx = 0.8, rely = 0.7, relwidth=0.1, relheight=0.125, anchor=CENTER)
ELBOW_label = tk.Label(lower_frame, text="Calculate Elbow Values", bg='#374785', fg="#CCCCCC", font=bodyFont)
ELBOW_label.place(relx = 0.15, rely = 0.7, anchor=W)
# calculate k-value
Kval_button = tk.Button(lower_frame, bg='#79B5A8', command=lambda: ss.calc_k(new_data))
Kval_button.place(relx = 0.8, rely = 0.9, relwidth=0.1, relheight=0.125, anchor=CENTER)
Kval_label = tk.Label(lower_frame, text="Show Those Elbows!",bg='#374785', fg="#CCCCCC", font=bodyFont)
Kval_label.place(relx = 0.15, rely = 0.9, anchor=W)

# ------------------ENTER K frame of GUI--------------------------------
final_frame = tk.Frame(root, bg='#374785', bd = 10)
final_frame.place(relx = 0.5, rely = 0.9, relwidth = 0.75, relheight=0.15, anchor=CENTER)

clusterFont = tkFont.Font(family="Helvetica", size=17)
entryFont = tkFont.Font(family="Helvetica", size=20,weight=tkFont.BOLD)

# enter the K-value and make those CLUSTERS!
enter_k = tk.Entry(final_frame, bg='#4E5F9C', fg='#CCCCCC',font=entryFont,justify="center")
enter_k.place(relx = 0.4, rely = 0.5, relwidth = 0.2, relheight = 0.8, anchor=CENTER)
submit_k_button = tk.Button(final_frame, bg='#A895CC', text="CLUSTER",font=clusterFont, command=lambda:ss.show_clusters(enter_k.get(),new_data))
submit_k_button.place(relx = 0.6, rely = 0.5, relwidth = 0.2, relheight = 0.8, anchor=CENTER)

# run this b-word
root.mainloop()

