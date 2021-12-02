import json, glob, os, tqdm, sys
import networkx as nx
import matplotlib.pyplot as plt
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

    for post in posts:
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

def extract_network_features(G):
    feature_dict = {"number_of_nodes": G.number_of_nodes(),
                    "number_of_edges": G.number_of_edges(),
                    "total_weight": G.size(weight="weight")}

    return feature_dict

def main():
    G_ = nx.Graph()
    acc_name_ = "krystal.jordan_"
    network_type_ = "comment"

    G_ = network(G_, acc_name_, network_type_)
    print(extract_network_features(G_))
#    save_as_gexf(G_, acc_name_, network_type_)

if __name__ == '__main__':

    main()
