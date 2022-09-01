# =========================
# Author: Kai Leon Deines
# =========================

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from colorama import Fore

import Generate

# set up driver
PATH = 'C:\\Program Files (x86)\\chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\\Users\\kai-leon.deines\\AppData\\Local\\Google\\Chrome\\UserDataSelenium")
driver = webdriver.Chrome(executable_path=PATH, options=options)

# set window size
driver.set_window_size(1920, 1080)
# load page
driver.get(
    'https://mybender.sharepoint.com/sites/BKGRD-FSPA/Bereichsveroeffentlichung/Lists/Prozesse/AllItems.aspx?viewid=cae6aa6f%2D69ca%2D4587%2D8cfd%2D04ae52829a8e')
# wait for page to load
time.sleep(2)

###################
# work from here
###################

tables = driver.find_elements(By.CSS_SELECTOR, '[data-automationid=main-app-content]')

print()

f = open('output.html', 'wb')
for table in tables:
    f.write(Generate.list_table(table).encode())

#f.write("<html><body>".encode() + driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML').encode() + "</body></html>".encode())
f.close()

driver.close()




