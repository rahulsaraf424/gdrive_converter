import os

from .base import FileFetcher
from utils import secure_filename

__author__ = 'Rahul Kumar Verma (rahulsaraf424@gmail.com)'


class DiskFileFetcher(FileFetcher):
    """A fetcher class that simply validates if the file is on disk"""

    def fetch(self, disk_path):
        """Pass through fetcher"""
        if not os.path.exists(disk_path):
            raise RuntimeError('Cannot find a file at path {}'.format(disk_path))
        return secure_filename(disk_path)
