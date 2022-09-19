# =========================
# Author: Kai Leon Deines
# =========================


from selenium import webdriver
from selenium.webdriver.common.by import By
from colorama import Fore


# methods
def reg_page(driver: webdriver):
    main_content = driver.find_element(By.CSS_SELECTOR, '[data-automation-id=contentScrollRegion]')
    title = main_content.find_element(By.CSS_SELECTOR, '[data-automation-id=TitleTextId]').text
    author = main_content.find_element(By.CSS_SELECTOR, '[data-automation-id=authorByLine]').text
    canvas = main_content.find_element(By.CSS_SELECTOR, '[data-automation-id=Canvas]')
    canvas_zones = canvas.find_elements(By.CSS_SELECTOR, '[data-automation-id=CanvasZone]')
    for canvas_zone in canvas_zones:
        canvas_controls = canvas_zone.find_elements(By.CSS_SELECTOR, '[data-automation-id=CanvasControl]')
        for canvas_control in canvas_controls:
            print('placeholder')

    return {
        "title": title,
        "author": author,

    }


def list_table(driver: webdriver):
    # get data
    columns_header_columns = driver.find_elements(By.CSS_SELECTOR,
                                                  '[data-automationid=ColumnsHeaderColumn]')  # header columns
    details_rows = driver.find_elements(By.CSS_SELECTOR, '[data-automationid=DetailsRow]')  # rows
    details_row_cells = driver.find_elements(By.CSS_SELECTOR, '[data-automationid=DetailsRowCell]')  # cells

    # get number of rows and columns
    rows = len(details_rows) + 1
    cols = int(len(details_row_cells) / len(details_rows))
    # create table list
    print('Generating table:')
    table = [[]]

    for columns_header_column in columns_header_columns:
        table[0].append(columns_header_column.text)

    for row in range(1, rows):  # go through each row individually
        table.append([])  # add empty list for all cells of this row
        print(Fore.LIGHTYELLOW_EX + str(int(row / rows * 100)) + '%...' + Fore.LIGHTWHITE_EX)  # print out progress

        for col in range(0, cols):  # go through each column of this row individually
            # add empty list for all elements of this cell
            table[row].append([])

            # get all links that are in this cell
            links = details_row_cells[(row - 1) * cols + col].find_elements(By.TAG_NAME, 'a')

            # get content (text) that is in this cell # remove icon character if necessary
            content = details_row_cells[(row - 1) * cols + col].text.replace('', '', 1)

            # assign placeholders (from content) to their links and add element list containing the data
            while len(links) > 0:
                # separating placeholders by \n and appending next substring with corresponding link
                try:
                    table[row][col].append(
                        [content[0:content.index('\n', 0, len(content))], links[0].get_attribute('href')])
                except ValueError:
                    table[row][col].append([content[0:len(content)], links[0].get_attribute('href')])

                # cut content string
                try:
                    content = content[content.index('\n', 0, len(content)) + 1:len(content)]
                except ValueError:
                    content = ''

                # remove link from links
                links.pop(0)

            # in case there's content without links just append the content
            while content is not None:
                # append next substring from content
                try:
                    table[row][col].append([content[0:content.index('\n', 0, len(content))]])
                except ValueError:
                    table[row][col].append([content[0:len(content)]])
                # cut content string
                try:
                    content = content[content.index('\n', 0, len(content)) + 1:len(content)]
                except ValueError:
                    content = None

    print(Fore.LIGHTGREEN_EX + 'Done' + Fore.WHITE)  # print out progress

    return table
