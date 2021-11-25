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
                    graph_.add_edge(hashtag_list[i], hashtag_list[j], weight=graph_[hashtag_list[i]][hashtag_list[j]]["weight"]+1)
                else:
                    graph_.add_edge(hashtag_list[i], hashtag_list[j], weight=1.0)
    return graph_

def save_as_gexf(graph, account_name, is_true = True):

    if is_true:
        nx.write_gexf(graph, "{}/{}/{}_network.gexf".format(DATA_PATH_, account_name, account_name))

def main():
    G = nx.Graph()
    acc_name = "krystal.jordan_"
    posts = get_posts(acc_name)

    for post in posts:
        caption = posts[post]["upperdata"]["text"]
        post_hashtags = separate_hashtags(caption)

        if len(post_hashtags) > 0:
            G = create_network(G, post_hashtags)

    save_as_gexf(G, acc_name)

if __name__ == '__main__':

    main()
