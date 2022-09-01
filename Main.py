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

"""
# get data
columnsHeaderColumns = driver.find_elements(By.CSS_SELECTOR, '[data-automationid=ColumnsHeaderColumn]') # header columns
columnsHeaderColumns.pop(len(columnsHeaderColumns)-1)
detailsRows = driver.find_elements(By.CSS_SELECTOR, '[data-automationid=DetailsRow]') # rows
detailsRowCells = driver.find_elements(By.CSS_SELECTOR, '[data-automationid=DetailsRowCell]') # cells

# neuer ansatz: statt alle zellen nur die der jeweiligen zeile laden???

# get number of rows and columns
rows = len(detailsRows)
cols = int(len(detailsRowCells) / rows)

# create table list
print('Generating table:')
table = []

for row in range(0, rows): # go through each row individually
    table.append([]) # add empty list for all cells of this row
    print(Fore.LIGHTYELLOW_EX + str(int(row/rows*100)) + '%...' + Fore.LIGHTWHITE_EX) # print out progress

    for col in range(0, cols): # go through each column of this row individually
        table[row].append([]) # add empty list for all elements of this cell
        links = detailsRowCells[row * cols + col].find_elements(By.TAG_NAME, 'a') # get all links that are in this cell
        content = detailsRowCells[row * cols + col].text.replace('', '', 1) # get content (text) that is in this cell # remove icon character if necessary

        # assign placeholders (from content) to their links and add element list containing the data
        while len(links) > 0:
            #
            try:
                table[row][col].append(
                    [content[0:content.index('\n', 0, len(content))], links[0].get_attribute('href')])
            except:
                table[row][col].append([content[0:len(content)], links[0].get_attribute('href')])

            try:
                content = content[content.index('\n', 0, len(content)) + 1:len(content)]
            except:
                content = ''
            links.pop(0)

        while content is not None:
            try:
                table[row][col].append([content[0:content.index('\n', 0, len(content))]])
            except:
                table[row][col].append([content[0:len(content)]])
            try:
                content = content[content.index('\n', 0, len(content)) + 1:len(content)]
            except:
                content = None

print(Fore.LIGHTGREEN_EX + 'Done' + Fore.WHITE) # print out progress
print(table)

f = open('table_output.html', 'wb')

f.write('<html><meta charset="utf-8"><body><style> body,table,tr,td {font-family:"Arial";font-size:12px;} table, tr, td {border:1px solid black;border-collapse:collapse} </style><table>'.encode())

f.write('<tr>'.encode())
for columnsHeaderColumn in columnsHeaderColumns:
    f.write(('<th>' + columnsHeaderColumn.text.replace('', '', 1).replace('', '', 1).replace('', '', 1) + '</th>').encode())
f.write('</tr>'.encode())


for row in table:
    f.write('<tr>'.encode())
    row.pop(len(row)-1)
    for col in row:
        f.write('<td>'.encode())

        for e in col:

            if len(e) == 2:
                f.write(('<a href="' + str(e[1]) + '">' + str(e[0]) + '</a>\n').encode())
            else:
                f.write(('<p>' + str(e[0]) + '</p>\n').encode())

        f.write('</td>'.encode())

    f.write('</tr>'.encode())

f.write('</table></body></html>'.encode())
f.close()

"""




