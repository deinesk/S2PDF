# =========================
# Author: Kai Leon Deines
# =========================

from bs4 import BeautifulSoup
from selenium import webdriver
import os
import json
from time import sleep
import random
import string

import pdftest


def get_page(page_id):
    for page in layout["pages"]:
        if page["id"] == page_id:
            return page
    return None


def append_page(page_id, ignore_children):
    # validating page
    page = get_page(page_id)
    if page is None:
        print("WARNUNG: Page " + str(page_id) + " konnte nicht gefunden werden")
        return
    url = page["url"]
    if url == "":
        print("WARNUNG: Die URL von Page " + str(page_id) + " konnte nicht gefunden werden")
        if not ignore_children:
            append_children(page)
        return

    # loading page
    print("Loading Page " + str(page_id) + " (" + page["label"] + "): " + url)
    html_source = load_page(url)

    # creating soup
    # also inserting page break at the beginning of each page
    soup = BeautifulSoup("<div class=\"pageBreak\" id=" + str(page_id) + ">" + html_source + "</div>", "html.parser")

    # manipulating soup
    add_reference(soup, page)
    decompose(soup, {'div[id="spCommandBar"]', 'div[id="CommentsWrapper"]', 'div[class="ReactFieldEditor-MoreToggle"]',
                     "i", "iframe"})
    decompose_third_parent(soup, {'div[class="ReactFieldEditor-placeHolder"]'})
    decompose_empty_buttons(soup)
    fix_headlines(soup)
    shift_headlines(soup, page)
    avoid_inside_page_breaks(soup)
    process_lists(soup)
    process_embeds(soup)
    process_images(soup)
    # process_embeds_as_pdf(soup) # won't be rendered by pdfkit

    # append the html to output
    with open("out/output.html", "a", encoding="utf-8") as file:
        file.write(str(soup))

    # do the same for each child
    if not ignore_children:
        append_children(page)


def read_pages(page_ids, ignore_children):
    for page_id in page_ids:
        append_page(page_id, ignore_children)


def update_references():
    with open("out/output.html", "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser", from_encoding="utf-8")

    update_a_tags(soup)
    update_buttons(soup)

    # removing the very first page break as it would otherwise cause an empty page at the beginning of the document
    soup.select('div[class="pageBreak"]')[0]["class"] = ""

    with open("out/output.html", "w", encoding="utf-8") as file:
        file.write(str(soup))


def update_a_tags(soup):
    # update hrefs in a-tags
    a_tags = soup.select("a")
    for a_tag in a_tags:
        href = a_tag["href"]
        try:
            reference_key = str(reference_map.get(href[href.index("/sites"):href.index(".aspx") + 11]))
            if reference_key != "None":
                a_tag["href"] = "#" + reference_key
                a_tag["target"] = "_self"
            else:
                a_tag.attrs.pop("href")
                if a_tag.text == "":
                    a_tag.decompose()
        except:
            a_tag.attrs.pop("href")
            if a_tag.text == "":
                a_tag.decompose()

def update_buttons(soup):
    # update buttons
    buttons = soup.select("button")
    for button in buttons:
        try:
            reference_key = str(reference_map.get(str(button["title"])))
        except:
            try:
                reference_key = str(reference_map.get(str(button["aria-label"])))
            except:
                reference_key = "None"
        if reference_key != "None":
            button["href"] = "#" + reference_key
            button.name = "a"


def decompose(soup, tag_names):
    # removing icons
    # when added again, they have to be added through list method
    for tag_name in tag_names:
        items = soup.select(tag_name)
        for item in items:
            item.decompose()


def decompose_third_parent(soup, tag_names):
    for tag_name in tag_names:
        items = soup.select(tag_name)
        for item in items:
            item.parent.parent.parent.decompose()


def decompose_empty_buttons(soup):
    # removing useless buttons
    buttons = soup.select("button")
    for button in buttons:
        if button.text == "":
            button.decompose()


def fix_headlines(soup):
    # creates headline tags where they're missing
    items = soup.select('div[data-automation-id="TitleTextId"]')
    for item in items:
        item.name = "h1"

    # role pages main headline
    bcbs = soup.select('ul[class="BreadcrumbBar-list"]')
    for bcb in bcbs:
        items = bcb.select("li")
        bcb.replace_with(BeautifulSoup("<h1>"+items[len(items)-1].text+"</h1>", "html.parser"))

    # role pages headlines
    items = soup.select("label")
    for item in items:
        item.name = "h2"


def shift_headlines(soup, page):
    # shifting headline levels
    if page["layer"] == 1:
        for i in range(5, 0, -1):
            headlines = soup.select("h" + str(i))
            for headline in headlines:
                headline.name = "h" + str(i + 1)
                # adding page break in case it originally was <h1>
                # if i == 1:
                #    headline["class"] = "pageBreak"


def process_images(soup):
    # saving and linking images
    images = soup.select('img')
    letters = string.ascii_lowercase
    for image in images:
        src = image["src"]
        if src == "":
            return
        try:
            driver.get(src)
        except:
            try:
                driver.get("https://mybender.sharepoint.com" + src)
                sleep(1)
            except:
                print("WARNUNG: Ungültiger Link '" + src + "'")

        img_id = ''.join(random.choice(letters) for _ in range(10))
        if not os.path.exists('out/media'):
            os.makedirs('out/media')
        with open("out/media/" + img_id + ".png", "wb") as png:

            try:
                png.write(driver.find_element_by_tag_name("img").screenshot_as_png)
            except:
                try:
                    png.write(driver.find_element_by_tag_name("svg").screenshot_as_png)
                except:
                    print("WARNUNG: Die Datei '" + src + "' konnte nicht gefunden werden.")
        image["src"] = "media/" + img_id + ".png"


def process_embeds(soup):
    # save and link embeds
    embeds = soup.select('div[data-automation-id="DocumentEmbed"]')
    for embed in embeds:
        iframes = embed.select('div[class="canvasWrapper"]')
        letters = string.ascii_lowercase
        for iframe in iframes:
            img_id = ''.join(random.choice(letters) for _ in range(10))
            with open("out/media/" + img_id + ".png", "wb") as png:
                png.write(iframe.screenshot_as_png)
                embed.replace_with(soup.new_tag('<img src="media/' + img_id + '.png"></img'))


def process_embeds_as_pdf(soup):
    # downloading and embedding pdfs
    embeds = soup.select('div[data-automation-id="DocumentEmbed"]')
    print(str(soup))
    for embed in embeds:
        print("EMBED")
        iframe = embed.select("iframe")[0]

        driver.get(iframe["src"])
        sleep(2)
        big_soup = BeautifulSoup(driver.page_source, "lxml")
        scripts = big_soup.find_all("script")
        for script in scripts:
            if ".spItemUrl" in script.text:
                data = script.text
                data = data[data.index(".spItemUrl"):len(data)]
                url = data
                data = data[data.index("\"path\":\"") + 8:len(data)]
                data = data[0:data.index("\"")]
                data = data.replace(" ", "%20")

                url = url[url.index("\"downloadUrl\":\"") + 15:len(url)]
                end = url.index("Bereichsveroeffentlichung") + 26
                url = url[0:end]

                print("Downloading: " + url + data)
                driver.get(url + data)
                sleep(5)
                embed.replace_with(BeautifulSoup('<div style="aspect-ratio:0.82;width:30vw;overflow-y:hidden;'
                                                 'overflow-x:hidden"><embed src="media/'
                                                 + data[data.index("/") + 1:len(data)] +
                                                 '#view=FitV&toolbar=0&scrollbar=0"width="105%" '
                                                 'style="margin-left:-3%;margin-top:-1%;" height="105%" '
                                                 'type="application/pdf"></div>', "html.parser"))


def process_lists(soup):
    # converting lists
    list_web_parts = soup.select('div[data-automation-id="ListWebPart"]')
    for list_web_part in list_web_parts:
        table_html = BeautifulSoup("<html><body><table></table></body></html>", "html.parser")

        details_list = list_web_part.select('div[data-automation-id="detailsListContainer"]')[0]

        # filling table header
        details_header = details_list.select('div[data-automationid="DetailsHeader"]')[0]
        columns_header_columns = details_header.select('div[data-automationid="ColumnsHeaderColumn"]')
        thead = table_html.new_tag("thead")
        for columns_header_column in columns_header_columns:
            th = table_html.new_tag("th")
            th.string = columns_header_column.text
            thead.append(th)
        table_html.html.body.table.append(thead)

        # filling rows
        list_cells = details_list.select('div[data-automationid="ListCell"]')
        for list_cell in list_cells:
            tr = table_html.new_tag("tr")

            table_html.html.body.table.append(tr)
            rows = table_html.html.body.table.find_all("tr")

            # filling cells
            details_row_cells = list_cell.select('div[data-automationid="DetailsRowCell"]')
            for details_row_cell in details_row_cells:
                td_tag = table_html.new_tag("td")

                cell_html = BeautifulSoup(details_row_cell.encode_contents(encoding='utf-8'), "lxml",
                                          from_encoding='utf-8')

                buttons = cell_html.find_all("button")
                button_index = 0
                for button in buttons:
                    button.insert_after(cell_html.new_tag("br"))
                    button_index = button_index + 1

                td_tag.append(cell_html)
                rows[len(rows) - 1].append(td_tag)

        list_web_part.replace_with(table_html.html.body)


def avoid_inside_page_breaks(soup):
    # avoiding page breaks between related elements
    canvas_zones = soup.select('div[data-automation-id="CanvasZone"]')
    for canvas_zone in canvas_zones:
        canvas_zone["class"] = "avoidInsidePageBreak"

    canvas_controls = soup.select('div[data-automation-id="CanvasContol"]')
    for canvas_control in canvas_controls:
        canvas_control["class"] = "avoidInsidePageBreak"


def append_children(page):
    for child in page["children"]:
        append_page(child, False)


def set_up_driver():
    # driver setup
    path = "C:\\Program Files (x86)\\chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-data-dir=C:\\Users\\" + os.getenv('username') + "\\AppData\\Local\\Google\\Chrome\\UserDataS2PDF")
    options.add_experimental_option("prefs",
                                    {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
                                     # Disable Chrome's PDF Viewer
                                     "download.default_directory": os.path.dirname(
                                         os.path.abspath(__file__)) + "\\out/media\\",
                                     "download.extensions_to_open": "applications/pdf"})
    d = webdriver.Chrome(executable_path=path, options=options)
    d.maximize_window()
    return d


def add_reference(soup, page):
    # adding id references
    url = page["url"]
    phantom_url = None
    try:
        phantom_url = page["phantom-url"]
    except:
        pass
    page_id = page["id"]

    try:
        reference_map[str(url[str(url).index("/sites"):str(url).index(".aspx") + 11])] = page_id
        if phantom_url is not None:
            reference_map[str(phantom_url[str(phantom_url).index("/sites"):str(phantom_url).index(".aspx") + 11])] = page_id
    except:
        pass
    spans = soup.select("span")
    for span in spans:
        try:
            reference_map[str(span["title"])] = page_id
        except:
            pass

    title_divs = soup.select('div[data-automation-id="TitleTextId"]')
    for title_div in title_divs:
        try:
            title = str(title_div["title"])
            title = title[0:title.index(" ")]
            reference_map[title] = page_id
        except:
            pass


def load_page(url):
    driver.get(url)
    sleep(patience)
    try:
        html_source = driver.find_element_by_class_name("Files-content").get_attribute("innerHTML")
    except:
        try:
            html_source = driver.find_element_by_class_name("mainContent").get_attribute("innerHTML")
        except:
            html_source = driver.find_element_by_class_name("ReactClientForm").get_attribute("innerHTML")
    return html_source


if not os.path.exists('out'):
    os.makedirs('out')
# create new output file
with open("out/output.html", "w", encoding="utf-8") as output:
    output.write("<meta charset='utf-8'><link rel=\"stylesheet\" href=\"../style.css\">")

# read json file
with open("layout.json", "r", encoding="utf-8") as f:
    # returns json object as a dictionary
    layout = json.load(f)

patience = 6 # loading time for each page
driver = set_up_driver()
reference_map = {}
reference_map.setdefault("#")

read_pages([100, 200, 201, 202, 300, 301, 302, 400, 500], True)

update_references()

driver.quit()
f.close()

pdftest.convert_to_pdf()
