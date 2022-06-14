import os
import numpy as np

import config
import util

def preProcessImages(img_data : util.ImageCollection) -> np.array :
    '''
    Generates array of data that represents an images.
    '''
    img_count = len(img_data)
    averages = np.zeros(shape=(img_count, 3))

    # Computing a list of averages for the images
    for i in util.progressBar(range(img_count), name="Averages"):
        data = img_data.GetData(i)
        averages[i] = np.average(data, axis=(0,1))

    return averages

def main() -> None:
    '''
    Saves the data in a file for later use.
    Gets parameters from config.py.
    '''
    img_data = util.ImageCollection(maxSize=10).FromDir(config.image_dir)
    preprocessed = preProcessImages(img_data)
    np.savetxt(config.preprocessed_file, preprocessed, fmt="%f")

if __name__ == "__main__":
    main()

