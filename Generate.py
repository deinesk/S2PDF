# =========================
# Author: Kai Leon Deines
# =========================

from selenium import webdriver
from selenium.webdriver.common.by import By
from colorama import Fore


# methods
def list_table(driver: webdriver):
    # get data
    columns_header_columns = driver.find_elements(By.CSS_SELECTOR,
                                                  '[data-automationid=ColumnsHeaderColumn]')  # header columns
    details_rows = driver.find_elements(By.CSS_SELECTOR, '[data-automationid=DetailsRow]')  # rows
    details_row_cells = driver.find_elements(By.CSS_SELECTOR, '[data-automationid=DetailsRowCell]')  # cells

    # get number of rows and columns
    rows = len(details_rows)
    cols = int(len(details_row_cells) / rows)

    # create table list
    print('Generating table:')
    table = []

    for row in range(0, rows):  # go through each row individually
        table.append([])  # add empty list for all cells of this row
        print(Fore.LIGHTYELLOW_EX + str(int(row / rows * 100)) + '%...' + Fore.LIGHTWHITE_EX)  # print out progress

        for col in range(0, cols):  # go through each column of this row individually
            # add empty list for all elements of this cell
            table[row].append([])

            # get all links that are in this cell
            links = details_row_cells[row * cols + col].find_elements(By.TAG_NAME, 'a')

            # get content (text) that is in this cell # remove icon character if necessary
            content = details_row_cells[row * cols + col].text.replace('', '', 1)

            # assign placeholders (from content) to their links and add element list containing the data
            while len(links) > 0:
                # separating placeholders by \n and appending next substring with corresponding link
                try:
                    table[row][col].append(
                        [content[0:content.index('\n', 0, len(content))], links[0].get_attribute('href')])
                except:
                    table[row][col].append([content[0:len(content)], links[0].get_attribute('href')])

                # cut content string
                try:
                    content = content[content.index('\n', 0, len(content)) + 1:len(content)]
                except:
                    content = ''

                # remove link from links
                links.pop(0)

            # in case there's content without links just append the content
            while content is not None:
                # append next substring from content
                try:
                    table[row][col].append([content[0:content.index('\n', 0, len(content))]])
                except:
                    table[row][col].append([content[0:len(content)]])

                # cut content string
                try:
                    content = content[content.index('\n', 0, len(content)) + 1:len(content)]
                except:
                    content = None

    print(Fore.LIGHTGREEN_EX + 'Done' + Fore.WHITE)  # print out progress
    # print(table)

    # construct html table from list
    html = '<html><meta charset="utf-8"><body><style> body,table,tr,td {font-family:"Arial";font-size:12px;} ' \
           'table, tr, td {border:1px solid black;border-collapse:collapse;vertical-align:top;} </style><table>'

    # construct table header row
    html = html + '<tr>'

    for columns_header_column in columns_header_columns:
        html = html + '<th>' + columns_header_column.text.replace('', '', 1).replace('', '', 1).replace('', '',
                                                                                                        1) + '</th>'

    html = html + '</tr>'

    # fill in the cells
    for row in table:
        html = html + '<tr>'
        row.pop(len(row) - 1)  # remove the last cell from each row as it's always empty

        for col in row:
            html = html + '<td>'
            for e in col:
                # an element list contains only one or two items (content and/or link)
                if len(e) == 2:
                    html = html + '<a href="' + str(e[1]) + '">' + str(e[0]) + '</a>\n'
                else:
                    html = html + '<p>' + str(e[0]) + '</p>\n'

            html = html + '</td>'

        html = html + '</tr>'

    html = html + '</table></body></html>'

    return html
