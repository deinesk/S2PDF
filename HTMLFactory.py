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
from selenium.webdriver.common.keys import Keys
import pdfkit
import rotatescreen
import shutil
import pyautogui

appdata = os.getenv('LOCALAPPDATA')
desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
driver_path = "C:\\Program Files (x86)\\chromedriver.exe"
os.environ["PATH"] = driver_path + ";C:\\Program Files\\wkhtmltopdf\\bin"


class HTMLFactory:
    def __init__(self):
        self.screen = rotatescreen.get_primary_display()
        self.default_orientation = self.screen.current_orientation
        self.screen_data = self.screen.info["Monitor"]
        self.screen_x = self.screen_data[0]
        self.screen_y = self.screen_data[1]
        self.screen_width = self.screen_data[2]
        self.screen_height = self.screen_data[3]
        create_output_file()
        self.config = load_json_from_appdata("config.json")
        self.patience = float(self.config["patience"])
        self.version_filtering = bool(self.config["version-filtering"])  # muss in config aktualisiert werden
        self.only_full_versions = bool(self.config["only-full-versions"])
        self.layout = load_json_from_appdata("layout.json")
        self.source_map = {}
        self.reference_map = {}
        self.driver = self.set_up_driver()

    def set_up_driver(self):
        # driver setup
        options = webdriver.ChromeOptions()
        options.add_argument(
            "user-data-dir=C:\\Users\\" + os.getenv('username') + "\\AppData\\Local\\Google\\Chrome\\UserDataS2PDF")
        d = webdriver.Chrome(executable_path=driver_path, options=options)
        d.set_window_position(self.screen_x, self.screen_y)
        d.maximize_window()
        return d

    def generate_html(self):
        # TO-DO: later there will only be: self.append_page(0)
        for page_id in {0}:
            self.append_page(page_id, ignore_children=False)
        self.update_references()
        self.driver.quit()
        self.screen.rotate_to(self.default_orientation)

    def reload_app_data(self):
        self.config = load_json_from_appdata("config.json")
        self.patience = float(self.config["patience"])
        self.version_filtering = bool(self.config["version-filtering"])
        self.layout = load_json_from_appdata("layout.json")

    def append_page(self, page_id, ignore_children):
        # validating page
        # getting page by id (from json)
        page = self.get_page(page_id)
        if page is None:
            print("WARNING: Page " + str(page_id) + " could not be found")
            return
        # checking url
        url = page["url"]
        if url == "":
            print("WARNING: URL of page " + str(page_id) + " could not be found")
            if not ignore_children:
                self.append_children(page)
            return

        # getting and editing soup
        soup = self.get_page_content_as_soup(page)
        self.add_references(soup, page)
        decompose_artifacts(soup)
        fix_headlines(soup, page_id)
        shift_headlines(soup, page)
        fix_table_headers(soup)
        process_lists(soup)
        # old pos
        self.process_images(soup)
        self.process_embeds(soup)
        # new pos
        if self.version_filtering:
            filter_by_version(soup, self.only_full_versions)
        save_to_output(soup)

        # also appending each child
        if not ignore_children:
            self.append_children(page)

    def get_page(self, page_id):
        for page in self.layout["pages"]:
            if page["id"] == page_id:
                return page
        return None

    def get_page_content_as_soup(self, page):
        page_id = page["id"]
        url = page["url"]

        # loading page
        print("LOADING: Page " + str(page_id) + " '" + page["label"] + "': " + url)
        self.driver.get(url)
        sleep(self.patience)
        html_source = self.get_page_content()

        # create soup # and insert page-break (at the beginning of each page)
        return BeautifulSoup("<div class=\"pageBreak\" id=\"p" + str(page_id) + "\">" + html_source + "</div>",
                             "html.parser")

    def get_page_content(self):
        self.wait_for_login()
        self.rotate_to_portrait()
        self.scroll_down()
        self.wait_for_page_to_load()
        try:
            html_source = self.driver.find_element_by_class_name("Files-content").get_attribute("innerHTML")
        except:
            try:
                html_source = self.driver.find_element_by_class_name("mainContent").get_attribute("innerHTML")
            except:
                try:
                    html_source = self.driver.find_element_by_class_name("ReactClientForm").get_attribute("innerHTML")
                except:
                    html_source = ""
                    print("WARNING: Couldn't get page source")
        return html_source

    def scroll_down(self):
        pyautogui.moveTo(540, 960)
        try:
            body = self.driver.find_element_by_css_selector('div[data-automation-id="contentScrollRegion"]')
            for i in range(0, 100):
                body.send_keys(Keys.ARROW_DOWN)
                sleep(0.001)
        except:
            pass

    def rotate_to_portrait(self):
        if not self.default_orientation % 180 == 90:
            self.screen.rotate_to(90)

    def wait_for_login(self):
        while (len(self.driver.find_elements_by_class_name("login-paginated-page")) != 0) | \
                (len(self.driver.find_elements_by_css_selector('input[name="login"]')) != 0) | \
                (len(self.driver.find_elements_by_class_name("sign-in-box ext-sign-in-box fade-in-lightbox")) != 0) | \
                (len(self.driver.find_elements_by_id("lightbox")) != 0):
            print("INFO: Waiting for login")
            self.screen.rotate_to(self.default_orientation)
            sleep(10)

    def wait_for_page_to_load(self):
        while "Vorschau wird geladen" in self.driver.page_source:
            print("INFO: Page not fully loaded. Sleeping one second...")
            sleep(1)

    def append_children(self, page):
        for child in page["children"]:
            self.append_page(child, False)

    # media processing functions
    def add_references(self, soup, page):
        # getting urls
        url = page["url"]
        phantom_url = None
        try:
            phantom_url = page["phantom-url"]
        except:
            pass
        # getting page id
        page_id = page["id"]

        # adding urls to reference map
        try:
            self.reference_map[str(url[str(url).index("/sites"):str(url).index(".aspx") + 11])] = page_id
            if phantom_url is not None:
                self.reference_map[
                    str(phantom_url[str(phantom_url).index("/sites"):str(phantom_url).index(".aspx") + 11])] = page_id
        except:
            pass

        # adding the title of spans to reference map
        spans = soup.select("span")
        for span in spans:
            try:
                self.reference_map[str(span["title"])] = page_id
            except:
                pass

        # adding the title of title divs to reference map # this is for process-pages and only takes the process-id
        title_divs = soup.select('div[data-automation-id="TitleTextId"]')
        for title_div in title_divs:
            try:
                title = str(title_div["title"])
                title = title[0:title.index(" ")]
                self.reference_map[title] = page_id
            except:
                pass

    def process_images(self, soup):
        # saving and linking images
        images = soup.select('img')
        letters = string.ascii_lowercase
        for image in images:
            src = image["src"]
            if src == "":
                return
            type = src[len(src) - 3:len(src)]
            try:
                img_id = self.source_map[src]
            except:
                try:
                    self.driver.get(src)
                except:
                    try:
                        self.driver.get("https://mybender.sharepoint.com" + src)
                    except:
                        print("WARNING: Invalid URL '" + src + "'")

                img_id = ''.join(random.choice(letters) for _ in range(10))
                self.source_map[src] = img_id
                with open(desktop + "/S2PDF/media/" + img_id + ".png", "wb") as png:
                    try:
                        png.write(self.driver.find_element_by_tag_name("img").screenshot_as_png)
                    except:
                        try:
                            png.write(self.driver.find_element_by_tag_name("svg").screenshot_as_png)
                        except:
                            print("WARNING: The file '" + src + "' could not be found.")
            image["src"] = desktop + "/S2PDF/media/" + img_id + ".png"
            if type == "svg":
                image["width"] = "20px"

    def process_embeds(self, soup):
        # downloading and embedding pdfs
        embeds = soup.select('div[data-automation-id="DocumentEmbed"]')
        for embed in embeds:
            iframes = embed.select("iframe")
            letters = string.ascii_lowercase
            for iframe in iframes:
                self.driver.get(iframe["src"])
                sleep(1 + self.patience)
                img_id = ''.join(random.choice(letters) for _ in range(10))
                with open(desktop + "/S2PDF/media/" + img_id + ".png", "wb") as png:
                    try:
                        png.write(self.driver.find_element_by_class_name("canvasWrapper").screenshot_as_png)
                        embed.replace_with(soup.new_tag('img src="media/' + img_id + '.png"'))
                    except:
                        print("WARNING: Embedded PDF could not be saved")

    # media post-processing functions
    def update_references(self):
        with open(desktop + "/S2PDF/output.html", "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser", from_encoding="utf-8")

        self.update_a_tags(soup)
        self.update_buttons(soup)

        # removing the very first page break as it would otherwise cause an empty page at the beginning of the document
        soup.select('div[class="pageBreak"]')[0]["class"] = ""

        with open(desktop + "/S2PDF/output.html", "w", encoding="utf-8") as file:
            file.write(str(soup))

    def update_a_tags(self, soup):
        # update hrefs in a-tags
        a_tags = soup.select("a")
        for a_tag in a_tags:
            href = a_tag["href"]
            try:
                reference_key = str(self.reference_map.get(href[href.index("/sites"):href.index(".aspx") + 11]))
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

    def update_buttons(self, soup):
        # update buttons
        buttons = soup.select("button")
        for button in buttons:
            try:
                reference_key = str(self.reference_map.get(str(button["title"])))
            except:
                try:
                    reference_key = str(self.reference_map.get(str(button["aria-label"])))
                except:
                    reference_key = "None"
            if reference_key != "None":
                button["href"] = "#" + reference_key
                button.name = "a"


def load_json_from_appdata(filename):
    with open(appdata + "/S2PDF/" + filename, "r", encoding="utf-8") as f:
        d = json.load(f)
    f.close()
    return d


def create_output_file():

    # creating new output file
    with open(desktop + "/S2PDF/output.html", "w", encoding="utf-8") as output:
        output.write("<meta charset='utf-8'><link rel=\"stylesheet\" href=\"style.css\">")
        output.close()


def save_to_output(soup):
    with open(desktop + "/S2PDF/output.html", "a", encoding="utf-8") as file:
        file.write(str(soup))


# soup manipulation functions #
# decomposing functions
def decompose_artifacts(soup):
    decompose_tags(soup,
                   {'div[id="spCommandBar"]', 'span[class*="accessibleLabel"]', 'figcaption',
                    'div[id="CommentsWrapper"]',
                    'div[class="ReactFieldEditor-MoreToggle"]',
                    })
    decompose_empty_icons(soup)
    decompose_third_parent(soup, {'div[class="ReactFieldEditor-placeHolder"]'})
    decompose_empty_buttons(soup)


def decompose_tags(soup, tag_names):
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


# headline editing functions
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
        bcb.replace_with(
            BeautifulSoup("<h1 class=\"main-headline\">" + items[len(items) - 1].text + "</h1>", "html.parser"))

    # role pages headlines
    items = soup.select("label")
    for item in items:
        item.name = "h4"

    pages = soup.select('div[id="p' + str(page_id) + '"]') # there's a 'p' in front of the div id for the table filters
    for page in pages:
        soup.find("h1")["id"] = page_id

    caption_elements = soup.select('div[data-automation-id="captionElement"]')
    for caption_element in caption_elements:
        caption_element.find("span").name = "strong"


def shift_headlines(soup, page):
    # shifting headline levels
    if page["layer"] == 1:
        for i in range(5, 0, -1):
            headlines = soup.select("h" + str(i))
            for headline in headlines:
                headline.name = "h" + str(i + 1)


# table manipulation functions
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


def filter_by_version(soup, only_full_versions):
    tables = soup.select("table")
    for table in tables:
        if "Version" not in table.thead.text:
            return
        header_cells = table.select("th")
        version_col_index = 0
        for header_cell in header_cells:
            version_col_index = version_col_index + 1
            if header_cell.text == "Version":
                break

        rows = table.select("tr")
        for row in rows:
            cell = row.select("td")[version_col_index - 1]
            text = cell.text
            text = text[0:1]
            if only_full_versions:
                cell.string.replace_with(text + ".0")
            if text == "0":
                row.decompose()




