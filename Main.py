# =========================
# Author: Kai Leon Deines
# =========================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import ConvertToHTML
import Generate


# driver set up
print('setting up driver...')
s = Service('C:\\Program Files (x86)\\chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\\Users\\kai-leon.deines\\AppData\\Local\\Google\\Chrome\\UserDataSelenium")
options.add_argument("--headless")
driver = webdriver.Chrome(service=s, options=options)
# driver.set_window_size(1920, 1080) # window size
# load page
driver.get('https://mybender.sharepoint.com/sites/BKGRD-FSPA/Bereichsveroeffentlichung/Lists/Prozesse/AllItems.aspx'
           '?viewid=cae6aa6f%2D69ca%2D4587%2D8cfd%2D04ae52829a8e')
# time.sleep(2) # wait for page to load

###################
# work from here
###################

print('searching for tables...')
tables = driver.find_elements(By.CSS_SELECTOR, '[data-automationid=main-app-content]')
print('tables found!')

# write file
f = open('output.html', 'wb')
for table in tables:
    f.write(ConvertToHTML.list_table(Generate.list_table(driver)).encode())

f.close()

driver.close()
