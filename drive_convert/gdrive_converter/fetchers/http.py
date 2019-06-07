import logging
import os
import urllib2

from .base import FileFetcher
from utils import secure_filename

__author__ = 'Rahul Kumar Verma (rahulsaraf424@gmail.com)'

logger = logging.getLogger(__name__)


class HttpFileFetcher(FileFetcher):
    """A fetcher class that simply downloads the file by http
    request and validates if the file is on disk."""

    def fetch(self, url, filename):
        """Pass through fetcher."""
        file = urllib2.urlopen(url)
        file_data = file.read()
        with open(filename, 'wb') as f:
            f.write(file_data)

        if not os.path.exists(filename):
            raise RuntimeError('Downloaded file is not at this path '
                               '{}'.format(filename))
        return secure_filename(filename)
