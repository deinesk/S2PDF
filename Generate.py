# =========================
# Author: Kai Leon Deines
# =========================
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
import re

def last_tag(html: str):
    index = html.rfind("<")
    return html[index:html.find(">", index)]


def find_last_open_tag(html):
    lt = last_tag(html)
    while re.match(r"^(</)", lt):
        lt = last_tag(html[0:html.rfind(lt)])
    return lt


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
        elif child.get_attribute('class') == 'od-PdfViewer-container':
            html = html + str(child.get_attribute('innerHTML'))
        elif child.get_attribute('class') == "ReactFieldEditor-MoreToggle":
            html = html
        elif child.tag_name == "strong":
            lot = find_last_open_tag(html)
            html1 = html[0:html.rfind(lot)]
            html2 = html[html.rfind(lot):len(html)]
            html2 = html2.replace(child.text, '')
            html = html1 + html2

            parent = child.find_element(By.XPATH, "./..")
            html = html[0:html.rfind(parent.tag_name)] + html[html.rfind(parent.tag_name):len(html)].replace(child.text, "")

            html = html + '<strong style="font-weight:bold;">' + child.text
            html = childify(html, child)
            html = html + "</strong>"
        elif re.match(r"^h+", child.tag_name) or child.tag_name == "u" or child.tag_name == "p" or child.tag_name == "div" or child.tag_name == "label":
            html1 = html[0:html.rfind(">") + 1]
            html2 = html[html.rfind(">") + 1:len(html)]
            html2 = html2.replace(child.text, '')
            html = html1 + html2 + "<" + child.tag_name + ">" + child.text
            html = childify(html, child)
            html = html + "</" + child.tag_name + ">"
        elif child.tag_name == "i":
            html = html.replace(child.text, '')

        # TODO: div wird nicht ordnungsgemäß geschlossen / syntaxfehler

        # TODO: Bereich in dem nach child.text gesucht wird auf parent beschränken # bei kurzen EInträgen sonst ggf.
        #  ungewollte Löschung einzelner Worte aus anderen Inhalten
        elif child.tag_name == "ol" or child.tag_name == "ul" or child.tag_name == "li":
            html = html.replace(child.text, "")
            html = html + "<" + child.tag_name + ">" + child.text
            html = childify(html, child)
            html = html + "</" + child.tag_name + ">"
        elif child.tag_name == "table":
            html = html.replace(child.text, "")
            inner_html = str(child.get_attribute('innerHTML'))
            while inner_html.find('<td ') != -1:
                i = inner_html.find('<td ')
                a = inner_html[0:i+3]
                b = inner_html[inner_html.find('>', i+3):len(inner_html)]
                inner_html = a+b
            a = inner_html.find("<tr>")
            b = inner_html.find("</tr>")
            aa = inner_html[0:a]
            bb = inner_html[a:b].replace('<td>', '<th>')
            bb = bb.replace('</td>', '</th>')
            cc = inner_html[b+5:len(inner_html)]
            inner_html = aa+bb+cc
            html = html + "<table>" + inner_html + "</table>"
        elif child.tag_name == 'img':
            id = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
            with open("assets/" + id + '.png', 'wb') as f:
                f.write(child.screenshot_as_png)
            html = html + "<img src='assets/" + id + ".png'>"

    return html


# methods

def react_field_page(driver: webdriver):
    html = ''
    more_toggles = driver.find_elements(By.CLASS_NAME, 'ReactFieldEditor-MoreToggle')
    for more_toggle in more_toggles:
        more_toggle.click()

    react_fields = driver.find_elements(By.CSS_SELECTOR, '[data-automationtype=clientFormField]')
    for react_field in react_fields:
        html = html + '<div>'
        if react_field == react_fields[0]:
            html = html + '<h2>' + react_field.text.replace(react_field.find_element(By.TAG_NAME,'label').text, '') + '</h2>'
        else:
            html = childify(html, react_field)
        html = html + '</div>'


    return html


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
            except Exception:
                pass
            try:
                canvas_control.find_element(By.CSS_SELECTOR, '[data-viewport-id*=ListWebPart]')
                if len(html_sub) > 0:
                    html = html + html_sub[0]
                    html_sub.pop(0)
            except Exception:
                pass
            try:
                id = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
                with open("assets/" + id + '.png', 'wb') as f:
                    f.write(canvas_control.find_element(By.TAG_NAME, 'img').screenshot_as_png)
                html = html + "<img src='assets/" + id + ".png'>"
                # print("image found!")
                # image_source = image.get_attribute('data-sp-originalimgsrc')
                # TODO: add image
            except Exception:
                pass
            try:
                canvas_control.find_element(By.CSS_SELECTOR, '[data-automation-id=textBox]')
                text_box = canvas_control.find_element(By.CSS_SELECTOR, '[data-automation-id=textBox]')
                html = childify(html, text_box)

            except Exception:
                pass

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
    print('generating table...')
    table = [[]]

    for columns_header_column in columns_header_columns:
        table[0].append(columns_header_column.text)

    for row in range(1, rows):  # go through each row individually
        table.append([])  # add empty list for all cells of this row

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

    print('done')  # print out progress

    return table
