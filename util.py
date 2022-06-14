import os
import numpy as np
from PIL import Image

class ImageCollection:
    '''
    Represents a collection of images, handles managing memory
    as to not run out when dealing with too much data.
    '''
    def __init__(self, maxSize=5, image_paths=[]):
        self.image_paths = image_paths

        # Q impl
        self.q = []
        self.maxSize = maxSize

        self.loadedData = dict()

    def FromDir(self, image_dir):
        files = os.listdir(image_dir)
        self.image_paths = [os.path.join(image_dir, file) for file in files]
        return self

    def GetImageFile(self, image_id):
        fimage = Image.open(self.image_paths[image_id])
        return fimage

    def GetData(self, image_id):
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
        fimage = self.GetImageFile(image_id)
        self.loadedData[image_id] = np.asarray(fimage, dtype="float")
        fimage.close()

        return self.loadedData[image_id]

    def __len__(self):
        return len(self.image_paths)

# NOTE: StackOverflow post helped alot! Should prob. find it.
def progressBar(iterable, name="Progress"):
    '''
    Prints a progress bar.
    '''
    length = 50

    total = len(iterable)
    def printProg(iteration):
        filled = int(length * iteration // total)
        not_filled = length - filled
        bar = "|" + ("#" * filled) + ('-' * not_filled) + "|"
        print(name + ':', bar, iteration, '/', total, end='\r')

    printProg(0)
    for i, item in enumerate(iterable):
        yield item
        printProg(i+1)
    print()

