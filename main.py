import sys, time, os, glob, shutil
from optparse import OptionParser
import InstaScrape.Scrape as Scrp
import InstaScrape.AutoManu.AutoManu as AM
import Network.Create_network as ntwrk
import Feature_Extraction.Feature_Extraction as fe
from InstaScrape.Config.config import *
import networkx as nx
import numpy as np

def open_enviroment(browser_name):
    print("Opening browser")
    if browser_name == "Chrome":
        DRIVER_PATH = r"{}\chromedriver.exe".format(DRIVER_PATH_CHROME)

    elif browser_name == "Firefox":
        DRIVER_PATH = r"{}".format(DRIVER_PATH_FIREFOX)

    driver_ = AM.rq_login(DRIVER_PATH, SITE_, USERNAME_, PASSWORD_, browser_name)
    session_ = Scrp.connect_request(driver_)

    return driver_, session_

def scrape_an_account(driver_, acc_name, session_):

    Scrp.go_page(driver_, acc_name)

    if AM.isavailable(driver_):
        print("* Start scraping {}".format(acc_name))

        followers_ = AM.followers(driver_, acc_name)
        following_ = AM.followers(driver_, acc_name, format_="following")
        if followers_[acc_name]["is_private"] == False:
            posts = AM.scroll_and_save(driver_, 1)
            is_fail = Scrp.get_raw_data(posts, acc_name, SITE_, session_, followers_, following_)
            return is_fail, following_[acc_name]["is_private"], following_
        else:
            return False, following_[acc_name]["is_private"], following_

    else:
        following_ = {acc_name : {"is_private": True,
                                     "following": []}}
        return False, True, following_
def extract_features(acc_name):
    posts = []

    for file_path in glob.glob("{}/{}/raw/*.json".format(DATA_PATH_, acc_name)):
        if os.path.basename(file_path) == acc_name+".json":
            Scrp.get_page_data(file_path)
        else:
            posts.append(file_path)

    Scrp.get_post_data(posts, acc_name)

def deleteaccs(filename):

    with open("{}/{}".format(PATH_, filename)) as myfile:
        accs = myfile.readlines()[:-1]
        for acc in accs:
            shutil.rmtree("{}/{}".format(DATA_PATH_, acc.strip()))

def checkfolders():
    broken_accs = []
    for folder_path in glob.glob("{}/*".format(DATA_PATH_)):
        acc_name_ = os.path.basename(folder_path)
        posts_paths =  glob.glob("{}/{}/raw/*.json".format(DATA_PATH_, acc_name_))
        if len(posts_paths) <=1:
            broken_accs.append(acc_name_)
    return broken_accs

def main():

    parser = OptionParser()
    parser.add_option("-m", "--mode", help='The operation that you want to execute.',
            type="str", dest="mode", default="")
    parser.add_option("-a", "--acc", help='The name of the account that you want to scrape.',
            type="str", dest="account_name", default="")
    parser.add_option("-l", "--list", help='The path of the text file that contains names of accounts.',
            type="str", dest="text_path", default="")
    parser.add_option("-b", "--browser", help='Browser that you want to select.',
            type="str", dest="browser_name", default="Firefox")
    parser.add_option("-n", "--network", help='Network type that you want to create.',
            type="str", dest="network", default="all")

    parameters, args = parser.parse_args(sys.argv[1:])

    if parameters.mode == "Scrape":
        """
        Scrapes given account(s) name only.
            * Required parameters are "-m = Scrape, -a = ACCOUNT_NAME_1,[ACCOUNT_NAME_2] | -l = TEXT_PATH"
        """

        finished_files = [os.path.basename(file)[:-5] for file in glob.glob("{}/*/raw/*.json".format(DATA_PATH_))]
        finished_accounts = [os.path.basename(acc) for acc in glob.glob("{}/*".format(DATA_PATH_)) if os.path.basename(acc) in finished_files]

        if parameters.text_path == "":
            acc_list = (parameters.account_name).split(",")

        else:
            with open(parameters.text_path) as myfile:
                acc_list = myfile.readlines()

        driver, session = open_enviroment(parameters.browser_name)
        start_ = time.perf_counter()

        for account_name in acc_list:
            if account_name.strip() not in finished_accounts:
                wait_time = np.absolute(np.random.normal(loc=2, scale=1))
                is_fail_ = scrape_an_account(driver, account_name.strip(), session)
                if is_fail_:
                    break
                else:
                    finished_accounts.append(account_name.strip())
                    time.sleep(wait_time)
        stop_= time.perf_counter()
        print("Scraping was succesfull. It finished in {:.2f} seconds".format(stop_-start_))
        driver.close()

    elif parameters.mode == "Feature_Filter":
        """
        Creates json files for each post and account page that contains chosen informations only.
            * Required parameters are "-m = Feature_Filter, -a = ACCOUNT_NAME_1,[ACCOUNT_NAME_2] | -l = TEXT_PATH
        """

        if parameters.text_path == "":
            acc_list = (parameters.account_name).split(",")

        else:
            with open(parameters.text_path) as myfile:
                acc_list = myfile.readlines()

        for account_name in acc_list:
            extract_features(account_name.strip())

    elif parameters.mode == "Network":
        """
        Creates the network(s) of account(s) and saves them as gexf file.
            * Required parameters are "-m = Network, -a = ACCOUNT_NAME_1,[ACCOUNT_NAME_2] | -l = TEXT_PATH, -n = all | tag | hashtag | comment
        """

        finished_files = [os.path.basename(file)[:-5] for file in glob.glob("{}/*/raw/*.json".format(DATA_PATH_))]
        finished_accounts = [os.path.basename(acc) for acc in glob.glob("{}/*".format(DATA_PATH_)) if os.path.basename(acc) in finished_files]

        if parameters.text_path == "":
            acc_list = (parameters.account_name).split(",")

        else:
            with open(parameters.text_path) as myfile:
                acc_list = myfile.readlines()

        start_ = time.perf_counter()

        for account_name in acc_list:
            print("* Starting network creation of {}.".format(account_name))

            if parameters.network == "all":
                mynetworks = ["hashtag", "tag", "comment"]
                for network_type_ in mynetworks:
                    G_ = nx.Graph()
                    G_ = ntwrk.network(G_, account_name.strip(), network_type_)
                    ntwrk.save_as_gexf(G_, account_name.strip(), network_type_)

            else:
                G_ = nx.Graph()
                G_ = ntwrk.network(G_, account_name.strip(), parameters.network)
                ntwrk.save_as_gexf(G_, account_name.strip(), parameters.network)


        stop_= time.perf_counter()
        print("Network creation was succesfull. It finished in {:.2f} seconds".format(stop_-start_))

    elif parameters.mode == "Feature_Extraction":

        acc_list = []

        if parameters.text_path == "" and parameters.account_name != "":
            acc_list = (parameters.account_name).split(",")

        elif parameters.account_name == "" and parameters.text_path != "":
            with open(parameters.text_path) as myfile:
                acc_list = myfile.readlines()

        else:
            acc_list = [os.path.basename(x) for x in glob.glob(f"{DATA_PATH_}/*")]



        start_ = time.perf_counter()
        m_image, m_text = fe.get_the_models()

        for account_name in acc_list:
            fe.savefeas(m_image, m_text, account_name)


    elif parameters.mode == "Check":

        broken_list = checkfolders()
        with open("{}/Broken_accs.txt".format(PATH_), mode="w") as myfile:
            for acc in broken_list:
                myfile.write("{}\n".format(acc))

    elif parameters.mode == "Broken":
        deleteaccs(parameters.text_path)

    elif parameters.mode == "Autonomus_Scrape":

        driver, session = open_enviroment(parameters.browser_name)
        start_ = time.perf_counter()

        if parameters.account_name != "":
            wait_time = np.absolute(np.random.normal(loc=2, scale=1))
            is_fail_, is_private, followings = scrape_an_account(driver, parameters.account_name, session)
            if is_fail_ == False:
                with open(f"{PATH_}/scraped_users.txt", "w") as myfile:
                    myfile.write(parameters.account_name+"\n")
                with open(f"{PATH_}/users_to_scrape.txt", "w") as myfile:
                    for following in followings[parameters.account_name]["following"]:
                        myfile.write(following+"\n")
                time.sleep(wait_time)

        while True:
            myfile = open(f"{PATH_}/users_to_scrape.txt", "r")
            scraped_files = open(f"{PATH_}/scraped_users.txt", "r")
            all_followings = []
            all_scrapeds = []

            scraped_users_list = scraped_files.readlines()
            scraped_files.close()
            all_scrapeds = [x.strip() for x in scraped_users_list]

            accounts = myfile.readlines()
            myfile.close()
            all_followins = [x.strip() for x in accounts]

            for account in all_followins:
                if account not in all_scrapeds:
                    wait_time = np.absolute(np.random.normal(loc=2, scale=1))
                    is_fail_, is_private, followings = scrape_an_account(driver, account, session)
                    if is_fail_:
                        break
                    elif is_private:
                        print(f"{account} is a private account. Skipping...")
                        with open(f"{PATH_}/scraped_users.txt", "a") as scraped_files:
                            scraped_files.write(account+"\n")
                        continue
                    else:
                        with open(f"{PATH_}/scraped_users.txt", "a") as scraped_files:
                            scraped_files.write(account+"\n")

                        with open(f"{PATH_}/users_to_scrape.txt", "a") as myfile:
                            for following in followings[account]["following"]:
                                myfile.write(following+"\n")
                    time.sleep(wait_time)
            if is_fail_:
                break

        stop_= time.perf_counter()
        print("Scraping was succesfull. It finished in {:.2f} seconds".format(stop_-start_))
        driver.close()

if __name__ == '__main__':

    main()
