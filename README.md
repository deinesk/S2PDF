# S2PDF alpha 1.1
SharePoint to PDF Converter

## Requirements
- Chrome Web Driver
- selenium
- beautifulsoup4
- pdfkit

## Setup
- Download the latest version of [Chrome Web Driver](https://chromedriver.chromium.org/downloads) and move the .exe to `C:\Program Files (x86)`.
- Install selenium package using package manager or terminal:
    ```
    pip install selenium
    ```
- Install beautifulsoup4 package using package manager or terminal:
    ```
    pip install beautifulsoup4
    ```
- Install pdfkit package using package manager or terminal:
    ```
    pip install pdfkit
    ```



## Usage
1. Run [Main.py](Main.py) and log in using your credentials.
<br>__Note:__ When prompted, save your credentials to stay logged in
2. Optionally edit [layout.json](layout.json) to add/remove pages and order them.
3. Start the conversion by running [Main.py](Main.py). The output files can be found in `/out`.

## Hint
To keep conversion times short for testing purposes, not every page is included in the output. You can change this, however, by altering the function call of `read_pages()`.
Only selecting page 0 and setting `ignore_children` to `False` in the function call will output everything as it is defined in [layout.json](layout.json)

## Known Issues
- Images are low resolution
- Icons in tables are missing
- Sometimes a word appears two times in a row (like 'WordWord')
- Currently, there's no feature that allows to select which columns of a table should be visible
- Some content is weirdly positioned
- Some tables headers are still missing after page break