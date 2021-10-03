import sys, time, os
from optparse import OptionParser
import InstaScrape.Scrape as Scrp
import InstaScrape.AutoManu.AutoManu as AM
from InstaScrape.Config.config import *

def open_enviroment():

    print("Opening browser")
    DRIVER_PATH = r"{}\chromedriver.exe".format(DRIVER_PATH_)

    driver_ = AM.rq_login(DRIVER_PATH, SITE_, USERNAME_, PASSWORD_)
    session_ = Scrp.connect_request(driver_)

    return driver_, session_

def scrape_an_account(driver_, acc_name, session_):
    Scrp.go_page(driver_, acc_name)
    posts = AM.scroll_and_save(driver_, 1)

    os.chdir(DATA_PATH_)
    Scrp.get_page_data(SITE_, acc_name, session_)
    Scrp.get_post_data(posts, acc_name, session_)
    Scrp.get_raw_data(posts, acc_name, SITE_, session_)

def main():

    parser = OptionParser()
    parser.add_option("-m", "--mode", help='The operation that you want to execute.',
            type="str", dest="mode", default="")
    parser.add_option("-a", "--acc", help='The name of the account that you want to scrape.',
            type="str", dest="account_name", default="")
    parser.add_option("-l", "--list", help='The path of the text file that contains names of accounts.',
            type="str", dest="text_path", default="")

    parameters, args = parser.parse_args(sys.argv[1:])

    if parameters.mode == "Single":
        """
        Scrapes given account(s) name only.
            * Required parameters are "-m = Single, -a = ACCOUNT_NAME_1,[ACCOUNT_NAME_2]"
        """

        driver, session = open_enviroment()
        start_ = time.perf_counter()
        acc_list = (parameters.account_name+",").split(",")
        acc_list.pop()

        for account_name in acc_list:
            scrape_an_account(driver, account_name.strip(), session)
        stop_= time.perf_counter()
        print("Scraping was succesfull. It finished in {:.2f} seconds".format(stop_-start_))
        os.chdir(PATH_)

    elif parameters.mode == "Multiple":
        """
        Scrapes account(s) from given text file.
            * Each line must contain only one account name.
        """
        driver, session = open_enviroment()
        start_ = time.perf_counter()
        with open(parameters.text_path) as myfile:
            for account in myfile.readlines():
                scrape_an_account(driver, account.strip(), session)
        stop_= time.perf_counter()
        print("Scraping was succesfull. It finished in {:.2f} seconds".format(stop_-start_))
        os.chdir(PATH_)

if __name__ == '__main__':

    main()
