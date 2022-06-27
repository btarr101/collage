import json
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import progressbar
from PIL import Image
from defopt import run


def create_dictionary(image_paths: Iterable[Path]) -> dict[str, tuple[float, float, float]]:
    """
    Generates the average color of each image in an iterable of image paths,
    and returns a dictionary mapping each image to its average color.

    :param image_paths: collection of image paths to generate the averages of.
    :return: a dictionary from image path to average color in RGB format.
    """

    source_dict = dict()

    for image_path in progressbar.progressbar(list(image_paths)):
        image = Image.open(image_path, "r")
        # noinspection PyTypeChecker
        pixels = np.array(image)  # open the pixels as a numpy array bc/ calculating average is much faster

        average = tuple(np.average(pixels, axis=(0, 1)))  # tuple-ize the average so it can be stored in a json
        source_dict[str(image_path)] = average
        image.close()

    return source_dict


def main(*, image_dir: Path) -> None:
    """
    Generates the average color of each image in a directory and stores
    those values in a json.

    :param image_dir: the directory where the images are stored.
    """

    if not image_dir.exists():
        print(f"Error: {image_dir} directory does not exist! Sources not generated.")
        sys.exit(1)

    image_paths = image_dir.glob('*')

    print(f"Generating sources from {image_dir}:")
    source_dict = create_dictionary(image_paths)

    output = Path.cwd() / (image_dir.name + '.sources.json')

    with open(output, 'w') as source_json:
        json.dump(source_dict, source_json)
    print(f"\t-> Outputted to {output}")


if __name__ == "__main__":
    run(main)
