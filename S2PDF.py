# =========================
# Author: Kai Leon Deines
# =========================
import json
import tkinter as tk
import os
import pdfkit
import pyautogui
import shutil
import rotatescreen
from bs4 import BeautifulSoup
from HTMLFactory import HTMLFactory

# save desktop path
desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')

# save appdata path
appdata = os.getenv("LOCALAPPDATA")

# get screen information
screen = rotatescreen.get_primary_display()
default_orientation = screen.current_orientation


class GUI:

    # S2PDF.create_dirs_and_files()
    def __init__(self):
        create_missing_dirs_and_files()
        self.root = tk.Tk()
        self.root.iconbitmap("icon.ico")
        self.root.geometry("400x200")
        self.root.title("S2PDF")
        self.bgcolor = "#222"
        self.img = tk.PhotoImage(file="button.png")
        self.root["bg"] = self.bgcolor

        # button frame
        self.buttonframe = tk.Frame(self.root)
        self.buttonframe.columnconfigure(0, weight=1)
        self.buttonframe.columnconfigure(1, weight=1)

        self.btn1 = tk.Button(self.buttonframe, text="Edit Layout...", font=("Tahoma", 16), command=self.open_layout)
        self.btn1.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.btn2 = tk.Button(self.buttonframe, text="Edit Config...", font=("Tahoma", 16), command=self.open_config)
        self.btn2.grid(row=0, column=1, sticky=tk.W + tk.E)

        self.format_button(self.btn1)
        self.format_button(self.btn2)

        self.buttonframe.pack(fill="x")

        # buttons
        self.btn3 = tk.Button(self.root, text="Download Data", command=self.create_html)
        self.btn6 = tk.Button(self.root, text="Reset Tables", command=self.reset_tables)
        self.btn4 = tk.Button(self.root, text="Edit Tables...", command=self.open_tables)
        self.btn5 = tk.Button(self.root, text="Convert to PDF", command=self.convert)

        for btn in {self.btn3, self.btn4, self.btn5, self.btn6}:
            self.format_button(btn)

        self.btn3.pack(padx=10)
        self.btn6.pack(padx=10)
        self.btn4.pack(padx=10)
        self.btn5.pack(padx=10)

        self.root.mainloop()

    def format_button(self, button):
        # background
        button["image"] = self.img
        button["bg"] = self.bgcolor
        button["activebackground"] = self.bgcolor
        # text
        button["fg"] = "#cff"
        button["activeforeground"] = "#fff"
        button["border"] = "0"
        button["font"] = ("Tahoma, 12")
        button["compound"] = "center"

    def open_layout(self):
        os.startfile(appdata + "/S2PDF/layout.json")

    def open_config(self):
        os.startfile(appdata + "/S2PDF/config.json")

    def open_tables(self):
        if not os.path.isfile(appdata + "/S2PDF/tables.json"):
            generate_tables_json()
        try:
            os.startfile(appdata + "/S2PDF/tables.json")
        except:
            return

    def create_html(self):
        try:
            HTMLFactory.generate_html(HTMLFactory())
            generate_tables_json()
            pyautogui.alert(title="Success!", text="The SharePoint has been downloaded.")
        except Exception as ex:
            screen.rotate_to(default_orientation)
            pyautogui.alert(title="ERROR: Download failed", text=str(ex))


    def convert(self):
        apply_table_filters()
        try:
            pdf = pdfkit.from_file([desktop + "/S2PDF/filtered.html"], desktop + "/S2PDF/filtered_output.pdf",
                                   options={"enable-local-file-access": ""})
            pyautogui.alert(title="Done", text="The Sharepoint has been converted to PDF successfully!")
        except Exception as ex:
            pyautogui.alert(title="ERROR: Conversion Failed", text=str(ex))

    def reset_tables(self):
        generate_tables_json()
        # pyautogui.alert(title="Success!", text="Tables have been reset.")


def create_missing_dirs_and_files():
    # making sure necessary directories exist
    if not os.path.exists(desktop + '/S2PDF/media'):
        os.makedirs(desktop + '/S2PDF/media')
    if not os.path.exists(appdata + "/S2PDF"):
        os.makedirs(appdata + "/S2PDF")

    # copying stylesheet
    shutil.copyfile("style.css", desktop + "/S2PDF/style.css")

    # copying layout and config to appdata if not existing
    if not os.path.isfile(appdata + "/S2PDF/layout.json"):
        shutil.copyfile("layout.json", appdata + "/S2PDF/" + "layout.json")
    if not os.path.isfile(appdata + "/S2PDF/config.json"):
        shutil.copyfile("config.json", appdata + "/S2PDF/" + "config.json")


def generate_tables_json():
    only_full_versions = bool(read_config()["only-full-versions"])
    try:
        with open(desktop + "/S2PDF/output.html", "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
    except:
        pyautogui.alert(title="File not found", text="You have to download the SharePoint first.")
        return

    pages_ = {}
    pages = soup.find_all("div", recursive=False)
    for page in pages:
        page_id = page["id"]
        tables_ = {}
        tables = page.select("table")
        for table in tables:
            title = get_table_title(table)
            cols_ = {}
            cols = table.select("th")
            for col in cols:
                if only_full_versions & (col.text == "Geändert"):
                    cols_[cols.index(col)] = {"Title": col.text, "Visible": False}
                else:
                    cols_[cols.index(col)] = {"Title": col.text, "Visible": True}
            table_ = {"Title": title, "Columns": cols_}
            tables_[tables.index(table)] = table_
        try:
            title = page.find("h1").text
        except:
            title = page.find("h2").text
        pages_[page_id] = {"Title": title, "Tables": tables_}

    with open(os.getenv("LOCALAPPDATA") + "/S2PDF/tables.json", "w", encoding="utf-8") as f:
        json.dump(pages_, f, ensure_ascii=False, indent=2, sort_keys=False)


def get_table_title(soup):
    parent = soup
    while parent.get("data-automation-id") != "CanvasControl":
        parent = parent.parent

    for _ in range(5, 0, -1):
        h = parent.find("h" + str(_))
        if h is not None:
            text = h.text
            while "\u200b" in text:
                text = text.replace("\u200b", "")
            return text
    while parent.get("data-automation-id") != "CanvasZone":
        parent = parent.parent

    for _ in range(5, 0, -1):
        h = parent.find("h" + str(_))
        if h is not None:
            if h.text is not None:
                text = h.text
                while "\u200b" in text:
                    text = text.replace("\u200b", "")
                return text
    return "Unknown Title"


def apply_table_filters():
    # create tables.json if necessary
    if not os.path.isfile(appdata + "/S2PDF/tables.json"):
        generate_tables_json()
    # load filters from json
    with open(appdata + "/S2PDF/" + "tables.json") as f:
        filters = json.load(f)
        f.close()

    # load html
    with open(desktop + "/S2PDF/output.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    f.close()

    pages = soup.find_all("div", recursive=False)
    for page in pages:
        page_id = page["id"]
        tables = page.select("table")
        for table in tables:
            table_id = tables.index(table)
            current_filter = filters[str(page_id)]["Tables"][str(table_id)]["Columns"]

            header_cells = table.select("th")
            for header_cell in header_cells:
                header_cell_id = header_cells.index(header_cell)
                if not current_filter[str(header_cell_id)]["Visible"]:
                    header_cell.decompose()

            rows = table.select("tr")
            for row in rows:
                cells = row.select("td")
                for cell in cells:
                    cell_id = cells.index(cell)
                    if not current_filter[str(cell_id)]["Visible"]:
                        cell.decompose()

    # write html to new file
    with open(desktop + "/S2PDF/filtered.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    f.close()


def read_config():
    with open(appdata + "/S2PDF/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        f.close()
    return config


GUI()
