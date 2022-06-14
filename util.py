import os
import numpy as np
from PIL import Image


class ImageCollection:
    """
    Represents a collection of images, handles managing memory
    as to not run out when dealing with too much data.
    """

    def __init__(self, max_size=5, image_paths=None):
        if image_paths is None:
            image_paths = []
        self.image_paths = image_paths

        # Q impl
        self.q = []
        self.maxSize = max_size

        self.loadedData = dict()

    def from_dir(self, image_dir: str):
        """
        Creates an image collection from a directory.
        """
        files = os.listdir(image_dir)
        self.image_paths = [os.path.join(image_dir, file) for file in files]
        return self

    def get_image_file(self, image_id: int) -> Image:
        """
        Gets the file of an image.
        """
        fimage = Image.open(self.image_paths[image_id])
        return fimage

    def get_image_data(self, image_id: int) -> np.array:
        """
        Gets the raw data of an image.
        """
        # image already loaded
        if image_id in self.loadedData:
            return self.loadedData[image_id]

        # pop an image
        while len(self.q) >= self.maxSize:
            pop_id = self.q[-1]
            del self.loadedData[pop_id]
            self.q.pop()

        # load an unloaded image
        self.q.insert(0, image_id)
        fimage = self.get_image_file(image_id)
        self.loadedData[image_id] = np.array(fimage, dtype="float")
        fimage.close()

        return self.loadedData[image_id]

    def __len__(self) -> int:
        """
        Gets the number of elements in an image collection.
        """
        return len(self.image_paths)


# NOTE: StackOverflow post helped alot! Should prob. find it.
def progress_bar(iterable, name="Progress"):
    """
    Prints a progress bar.
    """
    length = 50

    total = len(iterable)

    def print_prog(iteration):
        filled = int(length * iteration // total)
        not_filled = length - filled
        bar = "|" + ("#" * filled) + ('-' * not_filled) + "|"
        print("\r", end="")
        print(name + ':', bar, iteration, '/', total, end="")

    print_prog(0)
    for i, item in enumerate(iterable):
        yield item
        print_prog(i + 1)
    print()
