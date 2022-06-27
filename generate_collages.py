import sys
from pathlib import Path

import numpy as np
from PIL import Image
from defopt import run
from progressbar import progressbar


def create_image(mapping: np.ndarray, image: Image) -> Image:
    """
    Generates an image from a map file.

    :param mapping: a mapping where the elements are paths to images.
    :param image: the image from which the target and hence the map was generated from,
                   essentially this is the image which the dimensions will be gotten from.
    :return: the collage generated from the map file.
    """

    tiles = Image.new(mode="RGB", size=image.size)

    # calculating dimensions of a sub-images
    sub_dim = (image.width // mapping.shape[1],  # X
               image.height // mapping.shape[0])  # Y

    for i in progressbar(range(mapping.shape[1] * mapping.shape[0])):
        r = y = i // mapping.shape[1]
        c = x = i % mapping.shape[0]

        with Image.open(mapping[(r, c)], "r") as sub_image:
            resized = sub_image.resize(sub_dim)

        top_left = (x * sub_dim[0], y * sub_dim[1])
        tiles.paste(resized, top_left)
        resized.close()

    collage = Image.blend(tiles, image, 0.5)
    return collage


def main(*, map_or_map_dir: Path, count: int = 0) -> None:
    """
    Generates collages from mapping file(s). If a directory is specified
    for MAP_OR_MAP_DIR then a directory of collages will be generated,
    otherwise a single collage image will be generated.

    :param map_or_map_dir: the directory of mapping or single map file.
    :param count: if greater than 0, then only generate collage for a COUNT of
                  maps with the smallest residuals. For example if you only want
                  the collage with the best residual set this to 1.
    """

    if not map_or_map_dir.exists():
        print(f"Error {map_or_map_dir} directory or file does not exist! Collages not generated.")
        sys.exit(1)

    if map_or_map_dir.is_dir():
        map_paths = list(map_or_map_dir.glob('*'))
        out_dir = map_or_map_dir.with_name(map_or_map_dir.name[:-len('.maps')] + '.collages')
        if not out_dir.exists():
            out_dir.mkdir(exist_ok=False)
    else:
        map_paths = [map_or_map_dir]
        out_dir = Path('.')

    # curating a list of the lowest residuals
    if count != 0:
        map_paths.sort(key=lambda x: np.load(x, allow_pickle=True)['sos'])
        map_paths = map_paths[:count]

    for i, map_path in enumerate(map_paths):

        print(f"Generating collage from {map_path} ({i+1} of {len(map_paths)}):")

        # noinspection PyTypeChecker
        with np.load(map_path, allow_pickle=True) as npz:
            mapping = npz['arr']  # load mapping
            label = npz['label']  # load label
            image = Image.open(str(label), "r")

        collage = create_image(mapping, image)
        collage_path = out_dir / (map_path.name[:-len('.jpg.map.npz')] + '.collage.jpg')
        collage.save(collage_path, format='JPEG')
        print(f"\t-> Outputted to {collage_path}.")


if __name__ == "__main__":
    run(main)
