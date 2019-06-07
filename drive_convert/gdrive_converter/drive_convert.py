import io
import logging
import os
import pathlib
import re
import requests
import yaml
from uuid import uuid4

from apiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account

__author__ = 'Rahul Kumar Verma (rahulsaraf424@gmail.com)'

logger = logging.getLogger(__name__)


class GoogleDriveFileConverter:
    """Use google drive to export files to a different output format"""

    def __init__(self, service_account_file, s3_client=None):
        """Initialization."""

        self.service_account_file = service_account_file
        self.s3_client = s3_client
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/drive.file']
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file, scopes=SCOPES)
        self.drive_service = build('drive', 'v3', credentials=credentials)
        self.temp_dir = '/tmp'

    def get_file_extension(self, filename):
        """Given file name return the extension of the file.

        Parameters
        ----------
        filename: str
            The name of the file.

        Returns
        -------
        extension: str
            The extension of the file, None if filename is not valid.
        """
        if not isinstance(filename, str):
            return None

        # Get extension with `.`
        extension = pathlib.Path(filename).suffix

        # If empty string return None
        if not extension:
            return None
        else:
            return extension.replace('.', '')

    def list_all_files(self):
        """Return the list of all files."""

        results = self.drive_service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            logger.info('No files found.')
        else:
            logger.info('Files:')
            for item in items:
                logger.info(u'{0} ({1})'.format(item['name'], item['id']))

    def upload_file_to_drive(self, filename):
        """Upload the file to google drive in google doc format.

        Parameters
        ----------
        filename: str
            The name of the file.

        Returns
        -------
        extension: str
            The id of the file.
        """
        file_metadata = {
            'name': filename,
            'mimeType': 'application/vnd.google-apps.document'
        }

        media = MediaFileUpload(filename)
        file = self.drive_service.files().create(body=file_metadata,
                                                 media_body=media,fields='id').execute()
        return file.get('id')

    def delete_file(self, file_id):
        """Given file id to delete the file from google drive.

        Parameters
        ----------
        file_id: str
            The id of the file.

        Returns
        -------
        extension: str
            The message for successfully deleted the file.
        """
        self.drive_service.files().delete(fileId=file_id).execute()
        return file_id

    def upload_images_to_bucket(self, img_tags, bucket):
        """Upload the images to the s3 bucket.

        Parameters
        ----------
        img_tags: list
            The list of image sources.
        bucket: str
            The name of s3 bucket.
        Returns
        -------
        extension: list
            The list of all image names as unique string.
        """
        img_keys = list()
        img_urls = [img_tag.split('src="')[1].split('"')[0] for img_tag in img_tags]
        for img_url in img_urls:
            img_key = str(uuid4())
            temp_pic_path = os.path.join(self.temp_dir, img_key)
            with open(temp_pic_path, 'wb') as handle:
                response = requests.get(img_url, stream=True)
                if not response.ok:
                    logger.info(response)
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)

            # Upload the pic to s3 bucket
            logger.info('Uploading the images from {} to s3 bucket '
                        '{}'.format(temp_pic_path, bucket))
            self.s3_client.upload_file(temp_pic_path, bucket, img_key)
            img_keys.append(img_key)

            # Now delete the picture
            os.unlink(temp_pic_path)
        return img_keys

    def handle_images(self, converted_filename, s3_path, bucket):
        """Handle the images after deleting the files from drive.

        Parameters
        ----------
        converted_filename: str
            The name of converted filename.
        s3_path: str
            The path of s3 where the images were stored.
        bucket: str
            The name of s3 bucket.
        Returns
        -------
        extension: list
            The list of all image names as unique string.
        """
        with open(converted_filename, 'r') as file:
            data = file.read()
            img_tags = re.findall(r'<\/?img[^>]*>', data)
            img_keys = self.upload_images_to_bucket(img_tags, bucket)

            # Replace the images source after conversion
            replaced_img_tags = list()
            for i, img_tag in enumerate(img_tags):
                src = img_tag.split('src="')[1].split('"')[0]
                new_src = img_tag.replace(src, '{}/{}'.format(s3_path, img_keys[i]))
                replaced_img_tags.append(new_src)

                if img_tag in data:
                    data = data.replace(img_tags[i], replaced_img_tags[i])

        write_file = open(converted_filename, 'w')
        write_file.write(data)
        write_file.close()
        return

    def convert(self, input_file, output_file):
        """Given input file and the file name to be exported in
        different format with extensions.

        Parameters
        ----------
        input_file: str
            The name of the input file.
        output_file: str
            The name of the file to be exported.

        Returns
        -------
        extension: str
            The message for successfully conversion of the file.
        """
        mimi_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'mime.yaml'))
        with open(mimi_path, 'r') as stream:
            try:
                mimi_types = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.error(exc)

        output_file_extension = self.get_file_extension(output_file)
        if output_file_extension in mimi_types.keys():
            file_id = self.upload_file_to_drive(input_file)

            # Converting the google doc to given format
            request = self.drive_service.files().export_media(fileId=file_id,
                                                              mimeType=mimi_types[output_file_extension])
            fh = io.FileIO(output_file, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
        else:
            logger.error('The given input file can not be converted.')
            return
