# S2PDF release 1.0
SharePoint to PDF Converter

## Requirements
- Chrome Browser
- Chrome Web Driver
- wkhtmltopdf

## Setup
- Download and install [Chrome Browser](https://www.google.com/chrome/de/download-chrome/?brand=YTUH&gclid=EAIaIQobChMIitaPlJPJ_QIVywEGAB1T_gBGEAAYASAAEgLlu_D_BwE&gclsrc=aw.ds). If it's already installed on your system, install updates if available.
- Download the corresponding version of [Chrome Web Driver](https://chromedriver.chromium.org/downloads) and move the .exe to `C:\Program Files (x86)`.
- Download and install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html).
  


## Usage
1. Run `S2PDF.exe` and log in using your credentials. Then grab a coffe and let the script do it's work. (takes about 3m 30s)
2. The generated files can be found on your Desktop in the `S2PDF` directory.
3. Optionally edit `layout.json` in the installation folder (usually its located at `C:\Program Files (x86)\S2PDF`) to add/remove pages and order them.
   - Each page has ta have a unique `id`. 
   - To be converted, it has to be added to the children of one of the other pages. Main pages are usually added to the `master page` at the beginning of the file
   - You also have to set the layer, which defines the size of the page's headlines. Currently supported layers are 0 (= regular page) and 1 (= sub page). Otherwise the table of contents will be messed up.


## Notice
The script should dynamically wait for all content of the page to be loaded. In case you still notice any  issues, please let me know. 


## Known Issues
- Currently, there's no feature that allows to select which columns of a table should be visible
- Some content is weirdly positioned
- There's no title page
- There's no dedicated table of contents
- The start page is not formatted correctly