import numpy as np
import json

import config
import util
import dropboxManager


def preprocess_images(images: dropboxManager.ImageCollection, prev: dict = dict()) -> dict:
    """
    Generates a dictionary of preprocessed image data loaded.
    @type images: dropboxManager.ImageCollection
    @param prev:
    """
    averages = prev.copy()

    # Computing a dictionary of averages for the images
    for filename in util.progress_bar(images.get_filenames(), name="Averages"):
        if filename in averages:
            continue
        data = images.get_image_nparray(filename)
        averages[filename] = tuple(np.average(data, axis=(0, 1)))

    return averages


def main() -> None:
    """
    Loads images from dropbox and saves preprocessed data in a json file for later use.
    """
    images = dropboxManager.ImageCollection(config.dbx_access_token, config.image_path, config.local_tmp_path)
    preprocessed = preprocess_images(images)

    with open(config.preprocessed_file, "w") as outfile:
        json.dump(preprocessed, outfile)


if __name__ == "__main__":
    main()
