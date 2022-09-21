# =========================
# Author: Kai Leon Deines
# =========================


from selenium import webdriver
from selenium.webdriver.common.by import By
from colorama import Fore
import re


def rfind_nth(string: str, substring: str, n: int):
    if n == 1:
        return string.rfind(substring)
    else:
        return string.rfind(substring, 0, rfind_nth(string, substring, n - 1))


def childify(html: str, web_element: webdriver):
    children = web_element.find_elements(By.XPATH, './*')
    for child in children:
        if child.tag_name == "a":
            if child.text != "":
                if html.rfind(child.text, html.rfind(">")):
                    child_index = html.find(child.text, html.rfind(">"))
                    html1 = html[0:child_index]
                    html2 = html[child_index + len(child.text):len(html)]
                    html = html1 + "<a href='#'>" + child.text + "</a>" + html2  # TODO: set link
                else:
                    html = html + "<a href='#'>" + child.text + "</a>"  # TODO: set link
        elif child.tag_name == "strong":
            html = html.replace(child.text, "")
            html = html + '<p style="font-weight:bold;">' + child.text + "</p>"

        elif re.match(r"^h+", child.tag_name) or child.tag_name == "u" or child.tag_name == "p" or child.tag_name == \
                "div" or child.tag_name == "ol" or child.tag_name == "ul" or child.tag_name == "li":
            html1 = html[0:html.rfind(">") + 1]
            html2 = html[html.rfind(">") + 1:len(html)]
            html2 = html2.replace(child.text, '')
            html = html1 + html2 + "<" + child.tag_name + ">" + child.text
            html = childify(html, child)
            html = html + "</" + child.tag_name + ">"

        elif child.tag_name == "table" or child.tag_name == "tbody" or child.tag_name == "tr":
            html = html.replace(child.text, "")
            html = html + "<" + child.tag_name + ">"
            html = childify(html, child)
            html = html + "</" + child.tag_name + ">"

        elif child.tag_name == "td":
            html1 = html[0:html.rfind(">") + 1]
            html2 = html[html.rfind(">") + 1:len(html)]
            html2 = html2.replace(child.text, '')
            if child.get_attribute("role") == "columnheader":
                html = html1 + html2 + "<th>" + child.text
            else:
                html = html1 + html2 + "<" + child.tag_name + ">" + child.text
            html = childify(html, child)
            if child.get_attribute("role") == "columnheader":
                html = html + "</th>"
            else:
                html = html + "</" + child.tag_name + ">"

    return html


# methods
def reg_page(driver: webdriver, html_sub: list[str]):
    page_header = driver.find_element(By.CSS_SELECTOR, '[data-automation-id=pageHeader]')
    title = page_header.find_element(By.CSS_SELECTOR, '[data-automation-id=TitleTextId]').text
    author = page_header.find_element(By.CSS_SELECTOR, '[data-automation-id=authorByLine]').text
    html = "<h1>" + title + "</h1>"
    html = html + "<p>" + author + "</p>"

    canvas = driver.find_element(By.CSS_SELECTOR, '[data-automation-id=Canvas]')
    canvas_zones = canvas.find_elements(By.CSS_SELECTOR, '[data-automation-id=CanvasSection]')

    for canvas_zone in canvas_zones:
        canvas_controls = canvas_zone.find_elements(By.CSS_SELECTOR, '[data-automation-id=CanvasControl]')
        for canvas_control in canvas_controls:
            try:
                canvas_control.find_element(By.CSS_SELECTOR, '[data-viewport-id*=DividerWebPart]')
                html = html + "<hr style='border-top:3px solid #111; border-radius:2px'>"
            except Exception as e:
                print(e)
            try:
                canvas_control.find_element(By.CSS_SELECTOR, '[data-viewport-id*=ListWebPart]')
                if len(html_sub) > 0:
                    html = html + html_sub[0]
                    html_sub.pop(0)
            except Exception as e:
                print(e)
            try:
                # image = canvas_control.find_element(By.TAG_NAME, "img")
                print("image found!")
                # image_source = image.get_attribute('data-sp-originalimgsrc')
                # TODO: add image
            except Exception as e:
                print(e)
            try:
                canvas_control.find_element(By.CSS_SELECTOR, '[data-automation-id=textBox]')
                text_box = canvas_control.find_element(By.CSS_SELECTOR, '[data-automation-id=textBox]')
                html = childify(html, text_box)

            except Exception as e:
                print(e)

    return html


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
