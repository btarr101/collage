import sys
from pathlib import Path

import numpy as np
from PIL import Image
from defopt import run
from progressbar import progressbar


def create_array(image: Image, side_count: int) -> np.ndarray:
    """
    Creates an array that represents the target colors for the image.

    :param image: the image to generate the target for
    :param side_count: the number of sub-targets that will line up on any side of the target,
           for example a side count of 4 would result in having 16 sub-targets because 4 x 4 is 16.
    :return: a numpy array (matrix) where each location specifies an average color.
    """

    target = np.zeros(shape=(side_count, side_count, 3), dtype=np.float64)

    # noinspection PyTypeChecker
    pixels = np.array(image)  # open the pixels as a numpy array bc/ calculating average is much faster

    # calculating dimensions of a sub-target
    sub_dim = (pixels.shape[0] // side_count,
               pixels.shape[1] // side_count)

    for r in range(side_count):
        for c in range(side_count):
            # block of pixels for the sub-target
            target_block = pixels[
                           r * sub_dim[0]:(r + 1) * sub_dim[0],
                           c * sub_dim[1]:(c + 1) * sub_dim[1]
                           ]
            # calculating the average for that bock
            target[r, c] = np.average(target_block, axis=(0, 1))

    image.close()

    return target


def main(*, image_or_image_dir: Path, side_count: int) -> None:
    """
    Generates target files for image(s). If a directory is specified
    for IMAGE_OR_IMAGE_DIR then a directory of targets will be generated,
    otherwise a single target will be generated.

    :param image_or_image_dir: the directory or specific image to generate target(s) for.
    :param side_count: the number of sub-targets that will line up on any side of the target,
           for example a side count of 4 would result in having 16 sub-targets because 4 x 4 is 16.
    """

    if not image_or_image_dir.exists():
        print(f"Error: {image_or_image_dir} directory or file does not exist! Targets not generated.")
        sys.exit(1)

    if image_or_image_dir.is_dir():
        image_paths = list(image_or_image_dir.glob('*'))
        out_dir = Path.cwd() / (image_or_image_dir.name+'.targets')
        if not out_dir.exists():
            out_dir.mkdir(exist_ok=False)
    else:
        image_paths = [image_or_image_dir]
        out_dir = Path.cwd()

    print(f"Generating targets from {image_or_image_dir}:")
    for image_path in progressbar(image_paths):
        image = Image.open(image_path, "r")
        arr = create_array(image, side_count)
        label = str(image_path)

        np.savez(out_dir / (image_path.name + '.target.npz'),
                 arr=arr,
                 label=label)
    print(f"\t-> Outputted to {out_dir if len(image_paths) > 1 else image_paths[0]}")


if __name__ == "__main__":
    run(main)
