<p align="center"><img src="https://raw.githubusercontent.com/deinesk/S2PDF/master/icon.ico" /></p>

# S2PDF
SharePoint to PDF Converter.

Latest release: 1.3

## Requirements
- Chrome Browser
- Chrome Web Driver
- wkhtmltopdf


## Setup
- Download and install [Chrome Browser](https://www.google.com/chrome/de/download-chrome/?brand=YTUH&gclid=EAIaIQobChMIitaPlJPJ_QIVywEGAB1T_gBGEAAYASAAEgLlu_D_BwE&gclsrc=aw.ds). If it's already installed on your system, install updates if available.
  - Navigate to the three dots in the top right corner -> settings -> about chrome. There you can see which version you have installed.
- Download the corresponding version of [Chrome Web Driver](https://chromedriver.chromium.org/downloads) and move the .exe to `C:\Program Files (x86)`.
- Download and install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) (64 Bit).
- Download and run S2PDF Setup
  


## Usage
1. Run S2PDF from desktop or start menu.
2. Click on "Download Data" to download the SharePoint's content. 
   - This may take a while, and you cannot use your computer.
3. Click on "Convert to PDF" to generate the final PDF which can be found in the S2PDF folder on your desktop.


## Configuration

All .json files can be opened via the application, so you dont have to search for them.

### config.json

- `patience` is an extra loading time for each page. By default, it's set to 0.8 seconds but depending on your internet connection you might want to increase it.
- `version-filtering` only includes those tuples of a table where the version is 1.0 or higher when enabled. To disable it, set it to `false`.
- `only-full-versions` rounds all versions of documents down to .0 (e.g. 3.2 becomes 3.0) and removes the "last edited" column, as the dates are no longer accurate. Like `version-filtering`, this is set to `true` by default.

### layout.json
The layout keeps track of all SharePoint pages that should be converted.

Each page has these attributes:

| Attribute  | Type     | Description                                  |
|:-----------|:---------|:---------------------------------------------|
| `id`       | `int`    | Unique ID                                    |
| `label`    | `string` | Name of the page, just to keep an overview   |
| `layer`    | `int`    | 0 = regular, 1 = indented (smaller headings) |
| `url`      | `string` | URL of the SharePoint page                   |
| `children` | `int[]`  | Contains the IDs of all subpages             |


At first the application reads the very first (master) page. As it has no URL, it'll skip to its children and read them one after another. Keep in mind that if one of those children has children itself, these are going to be appended before the next child of the master page will be. 

By default, the master page has the children `100` "Start", `200` "Prozesse", `300` "Prozessrollen", `400` "Vorlagen" and `500` "Methoden & Guidelines".
Each of these main pages reserves 99 IDs for its children (e.g. `201` to `299` are reserved for children of "Prozesse").

In order to add a new page, simply copy the very last page in the file (with curly brackets), which has the generic ID `1234` and edit the attributes according to the rules. Also remember to add its ID to the children of either the master page or another page that's an n-th child of the master page.

### tables.json
As soon as you've downloaded the SharePoint data, you may edit the tables. Just click on "Edit Tables...", edit the file and save it before closing.
The file lists each column for each table for each page. 

By default, all columns are visible but if you want any to not be visible in the final PDF, simply set its `Visible` attribute to `false`. You can also click on "Reset Tables" to make everything visible again (except for the "last edited" column in case `only-full-versions` is enabled, which is then invisible by default). 


## Notice
The script should dynamically wait for the main elements of each page to be loaded. If some images are blurry or content is missing, try to increase the `patience` value, as the default of 0.8 requires a fast internet connection and might be too low for your setup. A menu bar on top of rendered PDFs (BPMN) can also be caused by a poor internet connection / low `patience` value.

In case the application crashes while you're being authorized, try to save your credentials and restart the application.
