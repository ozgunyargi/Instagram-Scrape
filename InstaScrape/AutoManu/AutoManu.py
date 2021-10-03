from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

import time
import os
import wget
import sys

sys.path.append(os.getcwd())

from InstaScrape.Config.config import *

def open_site(path, site): # Opens site

#    options = Options()
#    options.headless = True
#    op = webdriver.ChromeOptions()
#    op.add_argument('headless')
    driver = webdriver.Chrome(path)
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

def rq_login(DRIVER_PATH, SITE_NAME, USERNAME, PASSWORD): # A function specified for Reqest_Scrape.py file

    driver = open_site(DRIVER_PATH, SITE_NAME)
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

if __name__ == "__main__":

    DRIVER_PATH = r"{}\chromedriver.exe".format(DRIVER_PATH_)
    SITE_NAME = SITE_

    USERNAME = USERNAME_
    PASSWORD = PASSWORD_

    SEARCH_KEY =PAGE_
    KEYWORD = "image"

    driver = open_site(DRIVER_PATH, SITE_NAME)
    login(USERNAME,PASSWORD, driver)
    not_now(driver)
    make_search(driver, SEARCH_KEY)
    scroll(driver, 4)
    posts = get_posts(driver)