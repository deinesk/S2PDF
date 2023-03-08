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
import pyautogui
from selenium.webdriver.common.keys import Keys
import pdfkit
import rotatescreen
import shutil
import pyautogui

screen = rotatescreen.get_primary_display()
desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
os.environ["PATH"] = "C:\\Program Files (x86)\\chromedriver.exe;C:\\Program Files\\wkhtmltopdf\\bin"
print("INFO: Environment variables have been set: " + os.environ.get("PATH"))


def get_page(page_id):
    for page in layout["pages"]:
        if page["id"] == page_id:
            return page
    return None


def append_page(page_id, ignore_children):
    # validating page
    page = get_page(page_id)
    if page is None:
        print("WARNING: Page " + str(page_id) + " could not be found")
        return
    url = page["url"]
    if url == "":
        print("WARNING: URL of page " + str(page_id) + " could not be found")
        if not ignore_children:
            append_children(page)
        return

    # loading page
    print("LOADING: Page " + str(page_id) + " '" + page["label"] + "': " + url)
    driver.get(url)
    sleep(patience)
    html_source = get_page_content()

    # creating soup
    # also inserting page break at the beginning of each page
    soup = BeautifulSoup("<div class=\"pageBreak\" id=" + str(page_id) + ">" + html_source + "</div>", "html.parser")

    # manipulating soup
    add_reference(soup, page)
    decompose(soup,
              {'div[id="spCommandBar"]', 'span[class*="accessibleLabel"]', 'figcaption', 'div[id="CommentsWrapper"]',
               'div[class="ReactFieldEditor-MoreToggle"]',
               })
    decompose_empty_icons(soup)
    decompose_third_parent(soup, {'div[class="ReactFieldEditor-placeHolder"]'})
    decompose_empty_buttons(soup)
    fix_headlines(soup, page_id)
    shift_headlines(soup, page)
    fix_table_headers(soup)
    # avoid_inside_page_breaks(soup)
    process_lists(soup)
    if filter_versions:
        filter_by_version(soup)
    filter_by_version(soup)
    process_images(soup)
    process_embeds(soup)

    # process_embeds_as_pdf(soup) # won't be rendered by pdfkit

    # append the html to output
    with open(desktop + "/S2PDF/output.html", "a", encoding="utf-8") as file:
        file.write(str(soup))

    # do the same for each child
    if not ignore_children:
        append_children(page)


def filter_by_version(soup):
    tables = soup.select("table")
    for table in tables:
        if "Version" not in table.thead.text:
            return
        header_cells = table.select("th")
        version_col_index = 0
        for header_cell in header_cells:
            version_col_index = version_col_index + 1
            if header_cell.text == "Version": break

        rows = table.select("tr")
        for row in rows:
            cell = row.select("td")[version_col_index-1]
            if ".0" not in cell.text:
                row.decompose()


def read_pages(page_ids, ignore_children):
    for page_id in page_ids:
        append_page(page_id, ignore_children)


def update_references():
    with open(desktop + "/S2PDF/output.html", "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser", from_encoding="utf-8")

    update_a_tags(soup)
    update_buttons(soup)

    # removing the very first page break as it would otherwise cause an empty page at the beginning of the document
    soup.select('div[class="pageBreak"]')[0]["class"] = ""

    with open(desktop + "/S2PDF/output.html", "w", encoding="utf-8") as file:
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


def decompose_empty_icons(soup):
    icons = soup.select("i")
    for icon in icons:
        if not icon.find("img"):
            icon.decompose()


def decompose_empty_buttons(soup):
    # removing useless buttons
    buttons = soup.select("button")
    for button in buttons:
        if button.text == "":
            button.decompose()


def fix_headlines(soup, page_id):
    # creates headline tags where they're missing
    items = soup.select('div[data-automation-id="TitleTextId"]')
    for item in items:
        item.name = "h1"
        # also adding text-align center to this headline
        item["class"] = "main-headline"

    # role pages main headline
    bcbs = soup.select('ul[class="BreadcrumbBar-list"]')
    for bcb in bcbs:
        items = bcb.select("li")
        # also adding text-align center to this headline
        bcb.replace_with(BeautifulSoup("<h1 class=\"main-headline\">" + items[len(items) - 1].text + "</h1>", "html.parser"))

    # role pages headlines
    items = soup.select("label")
    for item in items:
        item.name = "h4"

    pages = soup.select('div[id="' + str(page_id) + '"]')
    for page in pages:
        soup.find("h1")["id"] = page_id
        page["id"] = ""


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
        type = src[len(src) - 3:len(src)]
        try:
            img_id = source_map[src]
        except:
            try:
                driver.get(src)
            except:
                try:
                    driver.get("https://mybender.sharepoint.com" + src)
                except:
                    print("WARNING: Invalid URL '" + src + "'")

            img_id = ''.join(random.choice(letters) for _ in range(10))
            source_map[src] = img_id
            with open(desktop + "/S2PDF/media/" + img_id + ".png", "wb") as png:
                try:
                    png.write(driver.find_element_by_tag_name("img").screenshot_as_png)
                except:
                    try:
                        png.write(driver.find_element_by_tag_name("svg").screenshot_as_png)
                    except:
                        print("WARNING: The file '" + src + "' could not be found.")
        image["src"] = "media/" + img_id + ".png"
        if type == "svg":
            image["width"] = "20px"


def process_embeds(soup):
    # downloading and embedding pdfs
    embeds = soup.select('div[data-automation-id="DocumentEmbed"]')
    for embed in embeds:
        iframes = embed.select("iframe")
        letters = string.ascii_lowercase
        for iframe in iframes:
            driver.get(iframe["src"])
            sleep(1)
            img_id = ''.join(random.choice(letters) for _ in range(10))
            with open(desktop + "/S2PDF/media/" + img_id + ".png", "wb") as png:
                png.write(driver.find_element_by_class_name("canvasWrapper").screenshot_as_png)
                embed.replace_with(soup.new_tag('img src="media/' + img_id + '.png"'))


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
    canvas_controls = soup.select('div[data-automation-id="CanvasContol"]')
    for canvas_control in canvas_controls:
        canvas_control["class"] = "avoidInsidePageBreak"
    canvas_sections = soup.select('div[data-automation-id="CanvasSection"]')
    for canvas_section in canvas_sections:
        canvas_section["class"] = "avoidInsidePageBreak"

    canvas_zones = soup.select('div[data-automation-id="CanvasZone"]')
    for canvas_zone in canvas_zones:
        canvas_zone["class"] = "avoidInsidePageBreak"


def fix_table_headers(soup):
    tables = soup.select("table")
    for table in tables:
        tr = table.select("tr")[0]
        table_datas = tr.select("td")
        for table_data in table_datas:
            table_data.name = "th"
        thead = soup.new_tag("thead")
        thead.insert(0, tr)
        table.insert(0, thead)
        table.parent.parent.parent["class"] = "avoidInsidePageBreak"


def append_children(page):
    for child in page["children"]:
        append_page(child, False)


def set_up_driver():
    # driver setup
    path = "C:\\Program Files (x86)\\chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-data-dir=C:\\Users\\" + os.getenv('username') + "\\AppData\\Local\\Google\\Chrome\\UserDataS2PDF")
    # options.add_argument("window-position=420,-420")
    # options.add_experimental_option("prefs",{"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],"download.default_directory": os.path.dirname(os.path.abspath(__file__)) + "\\out/media\\","download.extensions_to_open": "applications/pdf"})
    d = webdriver.Chrome(executable_path=path, options=options)
    d.maximize_window()
    # d.set_window_size(1080, 1920)
    # d.set_window_position(420,-420)
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
            reference_map[
                str(phantom_url[str(phantom_url).index("/sites"):str(phantom_url).index(".aspx") + 11])] = page_id
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


def get_page_content():
    while (len(driver.find_elements_by_class_name("login-paginated-page")) != 0) | \
            (len(driver.find_elements_by_css_selector('input[name="login"]')) != 0) | \
            (len(driver.find_elements_by_class_name("sign-in-box ext-sign-in-box fade-in-lightbox")) != 0) | \
            (len(driver.find_elements_by_id("lightbox")) != 0):
        print("Waiting for login")
        screen.rotate_to(0)
        sleep(10)
    screen.rotate_to(90)
    scroll_down()
    while "Vorschau wird geladen" in driver.page_source:
        print("INFO: Page not fully loaded. Sleeping one second...")
        sleep(1)
    try:
        html_source = driver.find_element_by_class_name("Files-content").get_attribute("innerHTML")
    except:
        try:
            html_source = driver.find_element_by_class_name("mainContent").get_attribute("innerHTML")
        except:
            html_source = driver.find_element_by_class_name("ReactClientForm").get_attribute("innerHTML")

    return html_source


def scroll_down():
    pyautogui.moveTo(540, 960)
    try:
        body = driver.find_element_by_css_selector('div[data-automation-id="contentScrollRegion"]')
        for i in range(0, 100):
            body.send_keys(Keys.ARROW_DOWN)
            sleep(0.001)
    except:
        pass


def init():
    # making sure necessary directories exist
    if not os.path.exists(desktop + '/S2PDF/media'):
        os.makedirs(desktop + '/S2PDF/media')

    # creating new output file
    with open(desktop + "/S2PDF/output.html", "w", encoding="utf-8") as output:
        output.write("<meta charset='utf-8'><link rel=\"stylesheet\" href=\"style.css\">")
    output.close()

    # copying stylesheet
    shutil.copyfile("style.css", desktop + "/S2PDF/style.css")


#
try:
    # read json files
    with open("layout.json", "r", encoding="utf-8") as f:
        # returns json object as a dictionary
        layout = json.load(f)
        f.close()
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        f.close()
    patience = float(config["patience"])
    filter_versions = bool(config["filter_versions"])
    init()
    driver = set_up_driver()
    source_map = {}
    source_map.setdefault("#")
    reference_map = {}
    reference_map.setdefault("#")
    read_pages([0], False)
    update_references()
    driver.quit()
    screen.rotate_to(0)
    pdf = pdfkit.from_file([desktop + "/S2PDF/output.html"], desktop + "/S2PDF/output.pdf")
    pyautogui.alert(title="Done", text="The Sharepoint has been converted to PDF successfully!")
except Exception as ex:
    screen.rotate_to(0)
    pyautogui.alert(title="Error: Conversion Failed", text=str(ex))
