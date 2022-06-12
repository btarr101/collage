import numpy as np
from PIL import Image
import os

class ImageCollection:
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
        fimage = Image.open(self.image_paths[image_id])
        fimage.load()
        self.loadedData[image_id] = np.asarray(fimage, dtype="int32")

        return self.loadedData[image_id]

    def __len__(self):
        return len(self.image_paths)
