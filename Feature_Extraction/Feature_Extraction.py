from keras.applications.vgg16 import VGG16
from sentence_transformers import SentenceTransformer
import glob, os, json, sys
import numpy as np
import pandas as pd
import tensorflow as tf
import pickle
from scipy import spatial
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from tensorflow.keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
from sklearn.model_selection import train_test_split
from sklearn import svm
from tqdm import tqdm

sys.path.append(os.getcwd())
from InstaScrape.Config.config import *

def saveasjson(path, mydict_, update_=True):
    """
    Saves the features as a JSON file. You can either update
    the already existed file or ignore it and create uncreated files.
    """
    name = path + "/features.json"
    if update_:
        with open(name, "w") as myfile:
            json.dump(mydict_, myfile)
    else:
        if os.path.isfile(name) == False:
            with open(name, "w") as myfile:
                json.dump(mydict_, myfile)

def get_the_models():
    model_VGG16 = VGG16(include_top= False)
    model_BERT = SentenceTransformer('sentence-transformers/paraphrase-xlm-r-multilingual-v1')

    return model_VGG16, model_BERT

def getcosinesimilarities (list_):
    """
    Returns a list that contains the cosine similarity vectors of each comment pair.
    Returns 0 if there aren't any
    """
    results = []
    if len(list_) > 1:
        for i in range(len(list_)):
            for j in range(i+1, len(list_)):
                results.append(1-spatial.distance.cosine(list_[i], list_[j]))
        return sum(results)/len(results)
    else:
        return 1

def imagefeatures(model, image_p):
    """
    Extracts the image features by using VGG16 model (block5_pool)
    and returns the flattened version of feature tensor.
    """
    Image = image.load_img(image_p, target_size=(224,224))
    embeddings = image.img_to_array(Image)
    embeddings = np.expand_dims(embeddings, axis=0)
    embeddings = preprocess_input(embeddings)
    features = model.predict(embeddings)

    return features.flatten()

def text_features(model, post_path):
    post_name = os.path.basename(post_path)
    file = post_path[:post_path.index("images")]+post_name[:-4]+".json"

    with open(file) as myfile:
        data = json.load(myfile)
        caption_embedding = model.encode(data["upperdata"]["text"]).tolist()
        comments = [model.encode(data["comments"][comment]["text"]).tolist() for comment in data["comments"]]

    text_dict = {"caption": caption_embedding,
                 "comments": comments}

    return text_dict

def savefeas(image_model, text_model, acc_name):
    """
    Extracts the features of images/texts and saves them in the JSON file.
    """
    flag = True
    print("* Start Extracting Features of {}".format(acc_name))
    account_path = "{}/{}".format(DATA_PATH_, acc_name)
    account_dict = {}
    pbar = tqdm(glob.glob("{}/{}/images/*".format(DATA_PATH_, acc_name)))
    for post_path in pbar:
        post_name = os.path.basename(post_path)[:-4]
        try:
            pbar.set_description("  => Extracting features of {}: ".format(post_name))
            im_features = imagefeatures(image_model, post_path)
            temp_dict = text_features(text_model, post_path )
            account_dict[post_name] = {"image_features":im_features.tolist(),
                                       "text_features": temp_dict}
        except:
            print("Unkown error, acc name: {}, post: {}".format(acc_name, post_name))
            flag = False
        if flag:
            saveasjson(account_path, account_dict)
        flag = True

    return account_dict


def main():

    m_image, m_text = get_the_models()
    print(savefeas(m_image, m_text, "amu_media"))

if __name__ == '__main__':
    main()
