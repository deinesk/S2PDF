# S2PDF pre-alpha 1.0
SharePoint to PDF Converter

## Requirements
- Chrome Web Driver
- selenium
- pdfkit

## Setup
- Install the latest version of [Chrome Web Driver](https://chromedriver.chromium.org/downloads) in `C:\Program Files (x86)`.
- Install selenium package using package manager or terminal:
    ```
    pip install selenium
    ```
- Install pdfkit package using package manager or terminal:
    ```
    pip install pdfkit
    ```

## Usage
1. Run [Main.py](Main.py) and log in using your credentials.
<br>__Note:__ When prompted, save your credentials to stay logged in
2. Optionally edit [config.json](config.json) to add/remove pages and order them.
3. Start the conversion by running [Main.py](Main.py). The output files can be found in `\output`.
<br>__Note:__ This may take a while. You can minimize the Chrome window but do not close it. The program is done as soon as the window closes by itself.

## Known Issues
- Images & rendered PDFs not included
- List titles missing
- Links not working correctly
- No table of contents
- Sometimes an unknown icon appears
- Sometimes the first column of a table is empty