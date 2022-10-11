# Instagram Scraper With Additional Functionalities

This repository provides you a toolbox that you can use while scraping Instagram without any API key requried but an account.Beside scraping,
there are functionalities implemented in this repository that may be helpful for a user while making analysis on extracted data such as network creation tools.

*Note*: To use this repository, please do not use to install requirements via `reqirements.txt` and also define needed account informantions via `InstaScrape/Config/config.py`

## Usage
- Open terminal and change current working directory as cloned repository. Then, enter the following template:

`$python main.py -m <MODE> [-a <ACCOUNT_NAME> | -l <LIST_PATH>] -b <BROWSER_PATH> [-n <NETWORK_OPTION>] `

- You need to define mode to use this script. There are couple of options:
   - `Scrape`: Alows you to scrape the given account(s) page, as well as posts (at most 32). You may define de willing accounts by entering names of the accounts as:
     - `-a <ACCOUNT1>,<ACCOUNT2>...` or
     - you may define a text file that holds the account names as `-l <TEXTFILEPATH>`
   - `Feature_Filter`: Allows you to trim information and leave only neccesarry ones to overcome memory allocation.
   - `Network`: Allows you to create networks based on following options:
     - hashtags
     - commenters
     - tagged persons
   - `Feature_Extraction`: Extract embeddings from post images, captions, comments etc. by using pretrained VGG16 (image) and MiniLM-L6-v2 (text) models. Extracted embeddings are stored.
   - `Check`: Functionality that checks if scraping operation is executed without any issue.
   - `Broken`: Functionality that deletes corrupted files.
   - `Autonomus_Scrape`: Allows user to scrape Instagram continously. You first, need to define a starting account by entering the name of the account to `-a <ACCOUNT>`. After you define the starting point, the script continuously scrapes the first 10 followings and adds them to the route to be scraped next.

- Please note that you need to define the browser that you will use. There are two options: You may choose either **Chrome** or **Firefox** webdrivers. Add the willing option to `-b <BROWSERPATH>`
