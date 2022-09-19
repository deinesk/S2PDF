# =========================
# Author: Kai Leon Deines
# =========================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import ConvertToHTML
import Generate
import time
import json

# driver set up
print('setting up driver...')
s = Service('C:\\Program Files (x86)\\chromedriver.exe')
options = webdriver.ChromeOptions()
# TODO: provide 'empty' user profile
options.add_argument("user-data-dir=C:\\Users\\kai-leon.deines\\AppData\\Local\\Google\\Chrome\\UserDataSelenium")
# options.add_argument("--headless")
driver = webdriver.Chrome(service=s, options=options)
# driver.set_window_size(1920, 1080) # window size
# load page
# TODO: implement gui for entering url and config
# TODO: if unable to authorise, require user to log in once
#driver.get(
#    'https://mybender.sharepoint.com/sites/BKGRD-FSPA/Bereichsveroeffentlichung/SitePages/Prozessrollen.aspx?csf=1&web=1&e=mcAB0z')
#time.sleep(2)  # wait for page to load

###################
# work from here
###################

with open('config.json', 'r') as f:
    data = json.load(f)


def parse_list_page():
    # TODO: fix links
    # TODO: fix icons
    return ConvertToHTML.list_table(
        Generate.list_table(driver))


def parse_reg_page(html_sub):
    # TODO: add other elements
    # TODO: append html_sub if ListWebPart is found
    return ""


def parse_page(page):

    # TODO: document lists

    html_sub = []
    for sub in page['sub']:
        html_sub.append(parse_page(sub))

    driver.get(page['link'])
    time.sleep(2)
    # list page
    try:
        if driver.find_element(By.CSS_SELECTOR, '[data-automationid=main-app-content]'):
            print("helo")
            return parse_list_page()
    # regular page
    except:
        try:
            if driver.find_element(By.CSS_SELECTOR, '[data-automation-id=contentScrollRegion]'):
                return parse_reg_page(html_sub)

        except:
            print('no content found')


content = ""
for page in data['pages']:
   content = content + parse_page(page)




# write file
f = open('output.html', 'wb')
# print(data['pages'][0])
f.write(content.encode())

f.close()

driver.close()

