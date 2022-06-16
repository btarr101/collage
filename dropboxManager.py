import os

import dropbox
import dropbox.exceptions

from PIL import Image
import io

import numpy as np


class ImageCollection:
    """
    Represents a collection of images in the dropbox.
    """
    def __init__(self, access_token: str, path: str = '', cache_dir: str = 'tmp'):
        self.dbx = dropbox.Dropbox(access_token)
        self.path = path

        # load the cache
        self.cache_dir = cache_dir
        self.cached_filenames = set(os.listdir(cache_dir)).union(self.get_filenames())

    def get_filenames(self) -> set:
        """
        Fetches all the filenames in the collection
        """
        return {entry.name for entry in self.dbx.files_list_folder(self.path).entries}

    def get_image(self, filename: str) -> Image:
        """
        Fetches an image from the dropbox
        """

        # look in cache first
        if filename in self.cached_filenames:
            image = Image.open(os.path.join(self.cache_dir, filename))
            return image

        try:
            md, res = self.dbx.files_download(self.path + '/' + filename)
        except dropbox.exceptions.HttpError as err:
            print('HTTP error:', err)
            return None

        data = res.content
        image = Image.open(io.BytesIO(data))

        # caching
        image.save(os.path.join(self.cache_dir, filename))
        self.cached_filenames.add(filename)

        return image

    def get_image_nparray(self, filename: str) -> np.array:
        """
        Fetches an image and returns is as a float numpy array
        """
        return np.array(self.get_image(filename), dtype='float')

    def add_image(self, filename: str, image: Image) -> None:
        """
        Adds an image to the collection/uploads it to dropbox.
        """
        with io.BytesIO() as output:
            image.save(output, format='JPEG')
            byte_arr = output.getvalue()

        try:
            res = self.dbx.files_upload(byte_arr, self.path + '/' + filename)
        except dropbox.exceptions.ApiError as err:
            print('API error:', err)
            return None

        print('uploaded as', res.name.encode('utf8'))
        return res
