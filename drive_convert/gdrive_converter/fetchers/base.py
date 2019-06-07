import abc

__author__ = 'Rahul Kumar Verma (rahulsaraf424@gmail.com)'


class FileFetcher(abc.ABC):

    @abc.abstractmethod
    def fetch(self, *args, **kwargs):
        """Load a return a pointer to the file"""
        raise NotImplementedError()
