# =========================
# Author: Kai Leon Deines
# =========================
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import ConvertToHTML
import Generate
import time
import json
import pdfkit

# driver set up
print('setting up driver...')
s = Service('C:\\Program Files (x86)\\chromedriver.exe')
options = webdriver.ChromeOptions()
# TODO: provide 'empty' user profile
options.add_argument("user-data-dir=C:\\Users\\" + os.getenv('username') + "\\AppData\\Local\\Google\\Chrome\\UserDataS2PDF")
# options.add_argument("--headless")
driver = webdriver.Chrome(service=s, options=options)
# driver.set_window_size(1920, 1080) # window size
# load page
# TODO: GUI
# TODO: login
# TODO: config editor (pages, subpages, table columns, save password?)

###################
# work from here
###################

with open('config.json', 'r') as f:
    data = json.load(f)


def parse_list_page():
    # TODO: fix icons
    return ConvertToHTML.list_table(
        Generate.list_table(driver))


def parse_reg_page(html_sub):
    return Generate.reg_page(driver, html_sub)


def parse_page(webpage):
    # TODO: document lists
    html_sub = []
    for sub in webpage['sub']:
        if sub != "":
            html_sub.append(parse_page(sub))

    if webpage['link'] != '':
        driver.get(webpage['link'])
    else:
        return
    time.sleep(2)
    # list page
    try:
        if driver.find_element(By.CSS_SELECTOR, '[data-automationid=main-app-content]'):
            return parse_list_page()
    # regular page
    except Exception as e:
        try:
            if driver.find_element(By.CSS_SELECTOR, '[data-automation-id=contentScrollRegion]'):
                return parse_reg_page(html_sub)

        except Exception as ee:
            print(ee)
            print('no content found')
        print(e)


content = '<html><meta charset="utf-8">'
for page in data['pages']:
    content = content + parse_page(page)
content = content + '</html>'

# write file
f = open('output/sharepoint_' + time.strftime("%Y%m%d_%H%M") + '.html', 'wb')
# print(data['pages'][0])
f.write(content.encode())
f.close()


driver.close()

# finally convert to pdf
pdfkit_path = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
pdfkit.from_file('output/sharepoint_' + time.strftime("%Y%m%d_%H%M") + '.html', 'output/sharepoint_' + time.strftime("%Y%m%d_%H%M") + '.pdf', configuration=pdfkit_path)
