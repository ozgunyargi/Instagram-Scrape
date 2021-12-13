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

def find_radius(G):
    try:
        return nx.radius(G)
    except:
        return np.nan
#    max(nx.connected_components(G), key=len) => another solution?

def find_max_core_number(G):
    mydict = nx.algorithms.core.core_number(G)
    max_core_number = max(nx.algorithms.core.core_number(G).values())

    counter = 0
    for node in mydict:
        if mydict[node] == max_core_number:
            counter += 1
    return counter

def extract_network_features(G):
    feature_dict = {"number_of_nodes": G.number_of_nodes(),
                    "number_of_edges": G.number_of_edges(),
                    "total_weight": G.size(weight="weight"),
                    "density": nx.classes.function.density(G),
                    "average_clustering_coefficient": nx.algorithms.cluster.average_clustering(G),
                    "radius":find_radius(G), # Hocaya danış
                    "maximum_clique_size": len(clique.max_clique(G)),
                    "number_of_connected_components": nx.number_connected_components(G),
                    "fraction_of_the_largets_connected_component": len(clique.max_clique(G))/G.number_of_nodes(),
                    "maximum_core_number": max(nx.algorithms.core.core_number(G).values()),
                    "number_of_nodes_that_has_maximum_core_number": find_max_core_number(G)
                    }

 # Density hesaplama, average clustering coefficient, radius of the network, maximum clique size, (error alırsan directed ı undirected a çevir), connected component sayısı, fraction of the largest connnected component (only ondirected network),
 # Maximum core number hesapla
 # Capture, recapture araştır
    return feature_dict

def main():
    G_ = nx.Graph()
    acc_name_ = "krystal.jordan_"
    network_type_ = "hashtag"

    G_ = network(G_, acc_name_, network_type_)
    print(extract_network_features(G_))
#    save_as_gexf(G_, acc_name_, network_type_)

if __name__ == '__main__':

    main()
