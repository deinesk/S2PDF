# S2PDF release 1.0
SharePoint to PDF Converter

## Requirements
- Chrome Browser
- Chrome Web Driver
- wkhtmltopdf

## Setup
- Download and install [Chrome Browser](https://www.google.com/chrome/de/download-chrome/?brand=YTUH&gclid=EAIaIQobChMIitaPlJPJ_QIVywEGAB1T_gBGEAAYASAAEgLlu_D_BwE&gclsrc=aw.ds). If it's already installed on your system, install updates if available.
  - Navigate to the three dots in the top right corner -> settings -> about chrome. There you can see which version you have installed.
- Download the corresponding version of [Chrome Web Driver](https://chromedriver.chromium.org/downloads) and move the .exe to `C:\Program Files (x86)`.
- Download and install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) (64 Bit).
- Run S2PDF Setup.
  


## Usage
1. Run `S2PDF`.
2. Click on `Download Data` to download the SharePoint's content.
3. Click on `Convert to PDF` to generate the final PDF which can be found in the S2PDF folder on your desktop.
### Optional
- Editing the config:
  - You may change the `patience` value, which defines an extra loading time for eah page. By default, it's set to 0.8 but depending on your internet connection you might want to increase it.
  - You can also enable/disable `version-filtering`, which only shows those entries in a table where the version ends with .0 (such as 1.0, 2.0, 3.0...)
- Editing the layout:
  - To add a page you have to copy another (with curly brackets) and give it a unique `id`, a `layer` (0 = main layer, 1 = indented layer) as well as an `url`. For it to be included in the conversion it has to be a child of either the "master" page or another page that's already a child of the master. For that, just add the new page's `id` to the children attribute of whatever page's child it should be.
- Editing tables:
  - As soon as the contents have been downloaded, you may edit the tables to select which columns of which tables should be (in)visible. By default, every column is visible. To change that, click on `Edit Tables...` and set the `Visible` attribute to `False` for all unwanted columns. 


## Notice
The script should dynamically wait for the main elements of the page to be loaded. In case you still notice any  issues, please let me know. If some images are blurry or content is missing, try to increase the `patience` value, as the default of 0.8 requires a fast internet connection and might be too low. A menu bar on top of rendered PDFs (BPMN) can also be caused by a poor internet connection / low `patience` value.

In case the application crashes while you're being authorized, try to save your credentials and restart the application.


## Known Issues
- There's no title page
- There's no dedicated table of contents
- The start page is not formatted correctly