# =========================
# Author: Kai Leon Deines
# =========================
import errno
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import ConvertToHTML
import Generate
import time
import json
import pdfkit
import ctypes

# driver set up
print('setting up driver...')
s = Service('C:\\Program Files (x86)\\chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument(
    "user-data-dir=C:\\Users\\" + os.getenv('username') + "\\AppData\\Local\\Google\\Chrome\\UserDataS2PDF")
# options.add_argument("--headless")
driver = webdriver.Chrome(service=s, options=options)
driver.get('https://mybender.sharepoint.com/sites/BKGRD-FSPA/Bereichsveroeffentlichung')

loggedin = False
while not loggedin:
    try:
        driver.find_element(By.CSS_SELECTOR, '[id=O365_NavHeader]')
        loggedin = True
    except:
        time.sleep(2)

# TODO: GUI
# TODO: config editor (pages, subpages, table columns)

###################
# work from here
###################

# load config
with open('config.json', 'r') as f:
    data = json.load(f)

# get destination directory
dest = str(data['dest'])
if not re.search('/$', dest):
    dest = dest + '/'


def parse_page(webpage):
    # create list for parsed subpages
    html_sub = []
    for sub in webpage['sub']:
        if sub != "":
            # parse and append to list
            html_sub.append(parse_page(sub))

    # load webpage
    if webpage['link'] != '':
        driver.get(webpage['link'])
    else:
        return
    time.sleep(2)

    # identify page type
    if len(driver.find_elements(By.CSS_SELECTOR, '[data-automationid=main-app-content]')) != 0:
        # list page
        if len(driver.find_elements(By.CSS_SELECTOR, '[data-automationid=ColumnsHeaderColumn]')) != 0:
            return ConvertToHTML.list_table(Generate.list_table(driver))
        # react form page
        elif len(driver.find_elements(By.CLASS_NAME, 'ReactClientForm')) != 0:
            return Generate.react_field_page(driver)
    # regular page
    elif len(driver.find_elements(By.CSS_SELECTOR, '[data-automation-id=contentScrollRegion]')) != 0:
        return Generate.reg_page(driver, html_sub)
    else:
        print('no content found')

# parse html start
content = '<!DOCTYPE html>' \
          '<html>' \
            '<head>' \
                '<meta charset="utf-8">' \
                '<link rel="stylesheet" href="../style.css">' \
                '<title>SharePoint Abbild</title>' \
            '</head>' \
            '<body>'

# iterate through pages and parse content
for page in data['pages']:
    print('\033[94m' + str(int(data['pages'].index(page)/len(data['pages'])*100)) + "%" + '\033[0m')  # print progress to console
    content = content + parse_page(page)

# parse html end
content = content + '</body></html>'


# create destination directory if missing
try:
    os.makedirs(os.path.dirname(dest))
except OSError as exc:
    if exc.errno != errno.EEXIST:
        raise

# create filename
date_and_time = time.strftime("%Y%m%d_%H%M")  # save date and time for consistency
filename = 'sharepoint_' + date_and_time + '.html'  # create filename
print('Writing \033[93m' + filename + '\033[0m to \033[93m' + dest + '\033[0m...')  # print info to console

# write html file
f = open(dest + filename, 'wb')
f.write(content.encode())
f.close()

"""""
url_debug = 'https://mybender.sharepoint.com/sites/BKGRD-FSPA/Bereichsveroeffentlichung/Lists/Prozessrollen%20neu/DispForm.aspx?ID=8&'
driver.get(url_debug)
with open(dest + 'debug_' + date_and_time + '.html', 'wb') as f:
    f.write(driver.page_source.encode())
    f.close()
"""""
driver.close()


# finally convert to pdf
print('Converting HTML to PDF...')
pdfkit_path = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
pdfkit.from_file(dest + 'sharepoint_' + date_and_time + '.html', dest + 'sharepoint_' + date_and_time + '.pdf',
                 configuration=pdfkit_path)
print('\033[92mSuccessfully converted!!\033[0m')  # print info to console

# message box
ctypes.windll.user32.MessageBoxW(0, "Die Konvertierung der gewählten SharePoint-Seiten wurde erfolgreich abgeschlossen.", "Abgeschlossen", 0)
