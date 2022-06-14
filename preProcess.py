import numpy as np

import config
import util


def preprocess_images(img_data: util.ImageCollection) -> np.array:
    """
    Generates array of data that represents an images.
    """
    img_count = len(img_data)
    averages = np.zeros(shape=(img_count, 3))

    # Computing a list of averages for the images
    for i in util.progress_bar(range(img_count), name="Averages"):
        data = img_data.get_image_data(i)
        averages[i] = np.average(data, axis=(0, 1))

    return averages


def main() -> None:
    """
    Saves the data in a file for later use.
    Gets parameters from config.py.
    """
    img_data = util.ImageCollection(max_size=20).from_dir(config.image_dir)
    preprocessed = preprocess_images(img_data)
    np.savetxt(config.preprocessed_file, preprocessed, fmt="%f")


if __name__ == "__main__":
    main()
