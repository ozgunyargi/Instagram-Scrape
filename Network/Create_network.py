import json, glob, os, tqdm, sys
import numpy as np
import networkx as nx
from networkx.algorithms.approximation import clique
import matplotlib.pyplot as plt
from tqdm import tqdm
sys.path.append(os.getcwd())
from InstaScrape.Config.config import *

def separate_hashtags(txt):
    hashtags = []

    if txt.count("#") > 0:
        txt = txt[txt.index("#"):]
        txt = txt.replace ("\n", " ")
        txt_list = txt.split(" ")

        for element in txt_list:
            if "#" in element:
                hashtags.append(element)
# Average class coefficent, networkx metricsleri bak, indegree centrality, random walk centrality
    return hashtags

def get_posts(acc_name):
    post_dict = {}

    for accounts in glob.glob("{}/*".format(DATA_PATH_)):

        if acc_name in os.path.basename(accounts):

            for post_path in glob.glob("{}/*.json".format(accounts)):
                if  acc_name not in os.path.basename(post_path):
                    with open(post_path) as myfile:
                        post = json.load(myfile)
                        post_dict[os.path.basename(post_path)] = post
    return post_dict

def create_network(graph_, hashtag_list):
    for hashtag in hashtag_list:
        if hashtag not in graph_:
            graph_.add_node(hashtag)

    if len(hashtag_list) > 1:
        for i in range(len(hashtag_list)-1):
            for j in range(i+1, len(hashtag_list)):
                if graph_.has_edge(hashtag_list[i], hashtag_list[j]):
                    graph_[hashtag_list[i]][hashtag_list[j]]["weight"] +=1
                else:
                    graph_.add_edge(hashtag_list[i], hashtag_list[j], weight=1.0)
    return graph_

def save_as_gexf(graph, account_name, network_type, is_true = True):

    if is_true:
        nx.write_gexf(graph, "{}/{}/{}_{}_network.gexf".format(DATA_PATH_, account_name, account_name, network_type))

def network(G, acc_name, network_type):

    posts = get_posts(acc_name)
    pbar = tqdm(posts)

    for post in pbar:
        if post[:-5] != "features" and post[:-5] != acc_name:
            pbar.set_description("  =>{} network creation of post {}".format(network_type, post[:-5]))
            network_elements = []
            if network_type == "hashtag":
                caption = posts[post]["upperdata"]["text"]
                network_elements = separate_hashtags(caption)
            elif network_type == "tag":
                for tagged in posts[post]["tags"]:
                    network_elements.append(posts[post]["tags"][tagged]["username"])
            elif network_type == "comment":
                    for commented in posts[post]["comments"]:
                        network_elements.append(posts[post]["comments"][commented]["user_info"]["username"])

            if len(network_elements) > 0:
                G = create_network(G, network_elements)

    return G

def capture_recapture(acc_name):
    posts = get_posts(acc_name)
    pbar = tqdm(posts)
    capture_recapture_dict = {}

    for post in pbar:
        ghost_dict = {}
        if post[:-5] != "features" and post[:-5] != acc_name:
            pbar.set_description("  =>{} collecting commenters of post {}".format(acc_name, post[:-5]))
            network_elements = []
            for commented in posts[post]["comments"]:
                network_elements.append(posts[post]["comments"][commented]["user_info"]["username"])
            ghost_dict["commenters"] = network_elements
            ghost_dict["number_of_comments"] = posts[post]["upperdata"]["comment_number"]
            ghost_dict["number_of_obsvrd_comments"] = len(posts[post]["comments"])
            capture_recapture_dict[post] = ghost_dict
    s_posts = list(capture_recapture_dict.keys())

    N_list = []

    for i in range(len(s_posts)-1):
        M = len(capture_recapture_dict[s_posts[i]]["commenters"]) # Total Marked
        T = len(capture_recapture_dict[s_posts[i+1]]["commenters"]) # Total capture on 2nd visit
        R = 0 # number "recaptured"
        for j in capture_recapture_dict[s_posts[i+1]]["commenters"]:
            if j in capture_recapture_dict[s_posts[i]]["commenters"]:
                R += 1
        if R == 0:
            M += 1
            T += 1
            R += 1
        N_list.append(M*T/R)

    print(N_list)

def find_radius(G):
    try:
        return nx.radius(G)
    except:
        return np.nan
    max(nx.connected_components(G), key=len)

def find_max_core_number(G):
    mydict = nx.algorithms.core.core_number(G)
    max_core_number = max(nx.algorithms.core.core_number(G).values())

    counter = 0
    for node in mydict:
        if mydict[node] == max_core_number:
            counter += 1
    return counter

def extract_network_features(graph):
    G = graph.copy()
    G.to_undirected()
    G.remove_edges_from(nx.selfloop_edges(G))

    number_of_nodes = G.number_of_nodes()
    number_of_edges =  G.number_of_edges()
    if number_of_nodes != 0:
        total_weight =  G.size(weight="weight")
        density =  nx.classes.function.density(G)
        acc = nx.algorithms.cluster.average_clustering(G)
        radius = nx.radius(G.subgraph(max(nx.connected_components(G), key=len)))
        mcs = len(clique.max_clique(G))
        ncc = nx.number_connected_components(G)
        flcc = len(max(nx.connected_components(G), key=len))/G.number_of_nodes()
        mcn = max(nx.algorithms.core.core_number(G).values())
        nnmcn = find_max_core_number(G)

    else:
        total_weight = 0
        density = 0
        acc = 0
        radius = 0
        mcs = 0
        ncc = 0
        flcc = 0
        mcn = 0
        nnmcn = 0

    feature_dict = {"number_of_nodes": number_of_nodes,
                    "number_of_edges": number_of_edges,
                    "total_weight": total_weight,
                    "density": density,
                    "average_clustering_coefficient": acc,
                    "radius":radius,
                    "maximum_clique_size": mcs,
                    "number_of_connected_components": ncc,
                    "fraction_of_the_largets_connected_component": flcc,
                    "maximum_core_number": mcn,
                    "number_of_nodes_that_has_maximum_core_number":nnmcn
                    }

 # Density hesaplama, average clustering coefficient, radius of the network, maximum clique size, (error alırsan directed ı undirected a çevir), connected component sayısı, fraction of the largest connnected component (only ondirected network),
 # Maximum core number hesapla
 # Capture, recapture araştır
    return feature_dict

def main():

    acc_name_ = "amu_media"
    network_types = ["hashtag","tag","comment"]

    for file_path in glob.glob(f"{DATA_PATH_}/*"):
        acc_name_ = os.path.basename(file_path)
        print(acc_name_)
        for network_type_ in network_types:
            G_ = nx.Graph()
            G_ = network(G_, acc_name_, network_type_)
            extract_network_features(G_)
#    capture_recapture(acc_name_)
#    save_as_gexf(G_, acc_name_, network_type_)

if __name__ == '__main__':

    main()
