from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Firefox

import time
import os
import wget
import sys
import json
import pandas as pd
from html.parser import HTMLParser

sys.path.append(os.getcwd())
from InstaScrape.Config.config import *

def open_site(path, site, browser_="Firefox"): # Opens site

    if browser_ == "Firefox":

        options = Options()
        options.add_argument("--headless")
        driver = Firefox(executable_path= DRIVER_PATH_FIREFOX, firefox_options=options)

    elif browser_ == "Chrome":

        driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get(site)
    return driver

def login (name, passwrd, driver): # Login to your account

    username = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

    username.clear()
    username.send_keys(name)
    password.clear()
    password.send_keys(passwrd)

    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

def not_now(driver): # click on not_now button

    not_now = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]'))).click()

def make_search(driver, key): # makes search on instagram search box
    searchbox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']")))
    searchbox.clear()

    searchbox.send_keys(key)

    time.sleep(5)
    searchbox.send_keys(Keys.ENTER)

def pull_data(driver): # Pulls metadata related with page

    over_list = []

    elements = driver.find_elements_by_css_selector("span[class='g47SY ']")

    for element in elements:
        over_list.append(element.text)

    return over_list

def scroll (driver, counter): # Scroll function

    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage or counter ==5:
            match=True
        counter += 1

def get_images(driver): # Saves img files

    images = driver.find_elements_by_tag_name('img')
    images = [image.get_attribute('src') for image in images]
    images = images[:-2]

    print('Number of scraped images: ', len(images))

    print(type(images))

    return images

def get_posts(driver): #Get post URL's

    posts = []
    links = driver.find_elements_by_tag_name('a')
    for link in links:
        post = link.get_attribute('href')
        if '/p/' in post:
          posts.append( post )

    return posts

def create_folder(foldername): # Create a folder named "foldername" if there aren't any

    path = os.getcwd()

    if not os.path.exists(path+r"/" + foldername):
        os.mkdir(path+r"/"+foldername)

def rq_login(DRIVER_PATH, SITE_NAME, USERNAME, PASSWORD, BROWSER): # A function specified for Reqest_Scrape.py file

    driver = open_site(DRIVER_PATH, SITE_NAME, browser_ = BROWSER)
    login(USERNAME,PASSWORD, driver)
    not_now(driver)

    return driver

def save_images(images,keyword): # Downloads the images
#requests
    path = os.getcwd()
    path = path + "/images"

    counter = 0
    for image in images:
        save_as = os.path.join(path, keyword + "_" + str(counter) + '.jpg')
        wget.download(image, save_as)
        counter += 1

def scroll_and_save(driver, counter): # Returns post URL's while scrolling down throught page to get more posts

    counted = 1
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    posts = []
    while(match==False):
        lastCount = lenOfPage
        time.sleep(3)

        links = driver.find_elements_by_tag_name('a')
        for link in links:
            post = link.get_attribute('href')
            if '/p/' in post and post not in posts:
              posts.append( post )

        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage or counted ==counter:
            match=True
        counted += 1

    return posts

def isavailable(driver):

#    driver.get(f"{SITE_}/{acc_name}")
    json_data = driver.find_element_by_xpath('/html/body/script[1]')
    string =json_data.get_attribute("innerHTML")
    json_file = json.loads(string[string.index("{"):-1])

    if 'HttpErrorPage' in list(json_file["entry_data"].keys()):
        return False

    else:
        return True

def followers(driver, acc_name, format_="follower"):

#    driver.get(f"{SITE_}/{acc_name}")
    usernames = []

    json_data = driver.find_element_by_xpath('/html/body/script[1]')
    string =json_data.get_attribute("innerHTML")
    json_file = json.loads(string[string.index("{"):-1])
    follower_num = json_file["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_followed_by"]["count"]
    following_num = json_file["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_follow"]["count"]
    is_private = json_file["entry_data"]["ProfilePage"][0]["graphql"]["user"]["is_private"]

    if format_ == "follower":
        num = follower_num

    else:
        num = following_num

    if is_private == False:
        if num > 0:
            if format_ == "follower":
                xpath = '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a'
                xpath_ff = 2
            else:
                xpath = '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a'
                xpath_ff = 3

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath))).click()

            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"/html/body/div[6]/div/div/div[{str(xpath_ff)}]/ul/div")))
            inner_element = element.find_elements_by_tag_name("li")
            for i in inner_element:
                username = i.find_element_by_tag_name("a").get_attribute("href").split("/")[-2]
                usernames.append(username)

            if format_ == "follower":
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[6]/div/div/div[1]/div/div[2]/button'))).click()

    follower_dict = {acc_name : {"is_private": is_private,
                                 format_: usernames}}
    return follower_dict

if __name__ == "__main__":

    DRIVER_PATH = r"{}\chromedriver.exe".format(DRIVER_PATH_CHROME)
    SITE_NAME = SITE_

    USERNAME = USERNAME_
    PASSWORD = PASSWORD_

    SEARCH_KEY =PAGE_
    account_name = "mitchdubin"

    driver_ = open_site(DRIVER_PATH, SITE_NAME, browser_="Chrome")
    login(USERNAME,PASSWORD, driver_)
    not_now(driver_)
    print(followers(driver_, account_name, format_="follower"))
    driver_.close()
