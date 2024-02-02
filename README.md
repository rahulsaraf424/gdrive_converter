## Google Drive File Converter

gdrive_converter provides a simple way to convert the file format programmatically.

### 1. Setup
Open your terminal and clone the repository by the command:

git clone https://github.com/rahulsaraf6212/gdrive_converter.git

Install the package by using pip command.

```
pip install gdrive_converter
```

### 2. How to use it ?
Create a service account from your google account and download the `credentials.json` file.

Import the module into your python file.

```
from drive_convert import gdrive_converter

//Create the instance by using credential file
drive = GoogleDriveFileConverter('<credential file path>')
```
Now, you can use the drive to list the files, delete it and convert it into any format.

