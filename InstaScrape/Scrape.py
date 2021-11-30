# import selenium,time & urllib modules
from selenium import webdriver
import time, urllib.request, requests, os, glob, sys
import json as js
from tqdm import tqdm

sys.path.append(os.getcwd())

import InstaScrape.AutoManu.AutoManu as Is
from InstaScrape.Config.config import *

def connect_request(browser):

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}

    s = requests.session()
    s.headers.update(headers)

    for cookie in browser.get_cookies():
        c = {cookie['name']: cookie['value']}
        s.cookies.update(c)

    print("* Login succesfull")
    return s

def go_page(driver, page): #Initialize the driver and open the related site


    driver.get(r"http://www.instagram.com/{}".format(page))

def get_page_data(page): #Get the metadata related with the opened page and save it as JSON

    acc_name = os.path.basename(page)[:-5]
    print("* Start Collection Metadata of {}".format(acc_name), end="", flush=True)

    metadict= {}

    with open(page) as myfile:
        json = js.load(myfile)

        names = ["id", "posts", "followers", "following", "full_name", "verified"]
        elements = []
        elements.append( int(json["logging_page_id"][json["logging_page_id"].index("_")+1:]) )
        elements.append(json["graphql"]["user"]["edge_owner_to_timeline_media"]["count"])
        elements.append(json["graphql"]["user"]["edge_followed_by"]["count"])
        elements.append(json["graphql"]["user"]["edge_follow"]["count"])
        elements.append(json["graphql"]["user"]["full_name"])
        elements.append(json["graphql"]["user"]["is_verified"])

        for id, name in enumerate(names):
            metadict[name] = elements[id]

        with open("{}/{}/{}.json".format(DATA_PATH_, acc_name, acc_name), 'w') as fp:
            js.dump(metadict, fp, indent=4)
            print(" => finished.".format(page))

def get_post_data(posts, acc): #Get post data and save it as JSON
    togo = []

    print("* Start scraping posts.")
    pbar = tqdm(posts)

    for post in pbar:
        pbar.set_description("  => Scraping post {}".format(os.path.basename(post)[:-5]))
        postdict = {}

        with open(post) as myfile:

            data = js.load(myfile)

            postdict["upperdata"] = get_upper_data(data)
            postdict["tags"] = get_tag_data(data)
            postdict["comments"] = get_comment_data(data)

            for tag in postdict["tags"]:

                if postdict["tags"][tag]["username"] not in togo:

                    togo.append(postdict["tags"][tag]["username"])

            get_images_videos(data, acc)

            with open('{}/{}/{}.json'.format(DATA_PATH_,acc,get_upper_data(data)["shortcode"]), 'w') as fp:
                js.dump(postdict, fp, indent=4)

    return togo

def get_upper_data(url): # Pulls metadata related with the page

    names = ["post_id", "shortcode", "is_video", "image_url", "text"]
    elements = []

    elements.append(int(url["graphql"]["shortcode_media"]["id"]))
    elements.append(url["graphql"]["shortcode_media"]["shortcode"])
    elements.append(url["graphql"]["shortcode_media"]["is_video"])
    elements.append(url["graphql"]["shortcode_media"]["display_url"])
    try:
        elements.append(url["graphql"]["shortcode_media"]["edge_media_to_caption"]["edges"][0]["node"]["text"])
    except:
        elements.append("")

    upperdata = {}

    for indx, name in enumerate(names):
        upperdata[name] = elements[indx]

    return upperdata

def get_tag_data(url): # Pulls the username info from each post

    tagdict = {}

    for tagged in url["graphql"]["shortcode_media"]["edge_media_to_tagged_user"]["edges"]:

        infodict = {}
        names = ["full_name","id","is_verified", "username"]

        path = tagged["node"]["user"]

        for name in names:
            infodict[name] = path[name]

        tagdict[infodict["full_name"]] = infodict

    return tagdict

def get_comment_data(url): # Pulls comments and information about commenters

    commentdict = {}

    for commenter in url["graphql"]["shortcode_media"]["edge_media_to_parent_comment"]["edges"]:

        upinfodict = {}
        names = ["post_id", "text", "spam?"]
        elements = ["id", "text", "did_report_as_spam"]

        for indx, name in enumerate(names):

            upinfodict[name] = commenter["node"][elements[indx]]

        upinfodict["likes"] = commenter["node"]["edge_liked_by"]["count"]

        userdict = {}

        names = ["user_id", "verified?", "username"]
        elements = ["id", "is_verified", "username"]

        for indx, name in enumerate(names):

            userdict[name] = commenter["node"]["owner"][elements[indx]]

        upinfodict["user_info"] = userdict

        commentdict[upinfodict["user_info"]["username"]] = upinfodict

    return commentdict

def get_raw_data(posts, page, site, s): # Pulls complete data related with post and saves it as JSON

    post_names = [os.path.basename(post) for post in glob.glob("{}/{}/raw/*.json".format(DATA_PATH_, page))]

    if not os.path.exists("{}/{}".format(DATA_PATH_,page)):
        os.mkdir("{}/{}".format(DATA_PATH_,page))
        os.mkdir("{}/{}/raw".format(DATA_PATH_,page))
        os.mkdir("{}/{}/images".format(DATA_PATH_,page))
        os.mkdir("{}/{}/videos".format(DATA_PATH_,page))

    URL = site + r"/" + page + r"/?__a=1"

    print("* Start scraping {}.".format(page))

    pbar = tqdm(posts)
    for post in pbar:
        shortcode = post.split("/")[-2]
        if shortcode+".json" not in post_names:
            r = s.get('{}?__a=1'.format( post ))
            data_json = r.json()

            with open('{}/{}/raw/{}.json'.format(DATA_PATH_,page,shortcode), 'w') as fp:
                pbar.set_description("  => Scraping post {}".format(post.split("/")[-2]))
                js.dump(data_json, fp, indent=4)

    if page+".json" not in post_names:
        r = s.get(URL)
        data_json = r.json()

        with open('{}/{}/raw/{}.json'.format(DATA_PATH_,page,page), 'w') as fp:
            js.dump(data_json, fp, indent=4)
            print("  => Account page scraping is finished!")

def get_images_videos(url, acc, download_video = False): # Saves images and videos

    path = os.getcwd()

    is_video = url["graphql"]["shortcode_media"]["is_video"]
    shortcode = url["graphql"]["shortcode_media"]["shortcode"]

    if is_video and download_video:

        os.chdir(r"{}\videos".format(path))
        curpath = os.getcwd()
        download_url = url["graphql"]["shortcode_media"]['video_url']

        try:
            urllib.request.urlretrieve(download_url, '{}/{}.mp4'.format(curpath, shortcode))

        except:

            pass
    else:

        download_url = url["graphql"]["shortcode_media"]['display_url']
        urllib.request.urlretrieve(download_url, '{}/{}/images/{}.jpg'.format(DATA_PATH_,acc,shortcode))

def text_to_list(file):

    file.seek(0)

    list_ = []

    for line in file:

        list_.append(line[:-1])

    return list_

if __name__ == "__main__":

    DRIVER_PATH = r"{}\chromedriver.exe".format(DRIVER_PATH_)
    SITE_NAME = SITE_

    USERNAME = USERNAME_
    PASSWORD = PASSWORD_

    PAGE = PAGE_

    driver = Is.rq_login(DRIVER_PATH, SITE_NAME, USERNAME, PASSWORD)

    session = connect_request(driver)

    counter = 0
    with open(r"D:\Users\suuser\Desktop\Experiment_small\Scraped\Scraped.txt", "a+") as scraped:
        scraped_ = text_to_list(scraped)
        for textfile in glob.glob(r"D:\Users\suuser\Desktop\Experiment_small\*.txt"):
            with open(textfile) as file:
                os.chdir(DATA_PATH_ + r"\{}".format(os.path.basename(textfile)[:-4]))
                for line in file:
                    if line.strip() not in scraped_:
                        go_page(driver, line.strip())
                        posts = Is.scroll_and_save(driver, 1)
                        get_page_data(SITE_, line.strip(), session)
                        get_post_data(posts, line.strip(), session)
                        scraped.write(line.strip() + "\n")
