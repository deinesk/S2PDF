# S2PDF release 1.0
SharePoint to PDF Converter

## Requirements
- Chrome Browser
- Chrome Web Driver
- wkhtmltopdf

## Setup
- Download and install [Chrome Browser](https://www.google.com/chrome/de/download-chrome/?brand=YTUH&gclid=EAIaIQobChMIitaPlJPJ_QIVywEGAB1T_gBGEAAYASAAEgLlu_D_BwE&gclsrc=aw.ds). If it's already installed on your system, install updates if available.
- Download the corresponding version of [Chrome Web Driver](https://chromedriver.chromium.org/downloads) and move the .exe to `C:\Program Files (x86)`.
  - Important: Open Chrome Browser and open settings. Navigate to "About Chrome" to see which version you need to download.
- Download and install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html).
- The environment variables no longer have to be set manually!
  


## Usage
1. Run `S2PDF.exe` and log in using your credentials. Then grab a coffe and let the script do it's work.
2. The generated files can be found on your Desktop in the `S2PDF` directory.
3. Optionally edit `layout.json` if you want to change the default layout (usually its located at `C:\Program Files (x86)\S2PDF`) to add/remove pages and order them. 
   - Each page has to have a unique `id`. 
   - To be converted, it has to be added to the children of one of the other pages. Main pages are usually added to the `master page` at the beginning of the file
   - You also have to set the layer, which defines the size of the page's headlines. Currently supported layers are 0 (= regular page) and 1 (= sub page). Otherwise, the table of contents will be messed up.
4. You may also want to edit `config.json` depending on the speed of your internet connection. By default, `patience` is set to 0.5, which is equivalent to 0.5 seconds loading time offset for each page. In the config you can also decide whether document versions should be filtered or not.


## Notice
The script should dynamically wait for the main elements of the page to be loaded. In case you still notice any  issues, please let me know. If some images are blurry or content is missing, try to increase the `patience` value, as the default of 0.5 requires a fast internet connection and might be too low. A menu bar on top of rendered PDFs (BPMN) can also be caused by a poor internet connection.


## Known Issues
- Currently, there's no feature that allows to select which columns of a table should be visible
- Some content is weirdly positioned
- There's no title page
- There's no dedicated table of contents
- The start page is not formatted correctly