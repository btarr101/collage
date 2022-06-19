import os.path

import numpy as np
from PIL import Image

import json

import config
import dropboxManager
import util


def gen_target(image: np.array, side_count: int) -> np.array:
    """
    Generates a target to collage for.
    """
    cnt = side_count ** 2
    target = np.zeros(shape=(cnt, 3), dtype='float')

    rows = len(image)
    cols = len(image[0])
    sub_rows = rows // side_count
    sub_cols = cols // side_count

    for i in range(cnt):
        r = i // side_count
        c = i % side_count

        block = image[r * sub_rows:(r + 1) * sub_rows, c * sub_cols:(c + 1) * sub_cols]
        target[i] = np.mean(block, axis=(0, 1))
    return target


def gen_map(target: np.array, averages: dict) -> list:
    """
    Generates a collage mapping for the target image.
    """
    target_cnt = len(target)

    residuals = [float('inf') for i in range(target_cnt)]
    index_map = np.full(shape=target_cnt, fill_value=-1, dtype='int')

    keys = list(averages.keys())
    averages_indexed = list(averages.values())
    image_q = list(range(len(averages)))

    while len(image_q) > 0:
        i = image_q.pop(0)
        avg = averages_indexed[i]

        best = -1
        best_residual = float('inf')

        for challenger, sub_target_avg in enumerate(target):
            challenger_residual = np.linalg.norm(sub_target_avg - avg)

            # if worse than best, skip
            if challenger_residual > best_residual:
                continue

            # if taken, skip if I'm a worse fit
            if index_map[challenger] != -1:
                if residuals[challenger] <= challenger_residual:
                    continue

            # update best
            best = challenger
            best_residual = challenger_residual

        # no target found
        if best == -1:
            continue

        # kick off other
        if index_map[best] != -1:
            image_q.append(index_map[best])

        # assign me
        index_map[best] = i
        residuals[best] = best_residual

    collage_map = [keys[index] for index in index_map]
    return collage_map


def gen_tiles(shape: tuple, collage_map: list, images: dropboxManager.ImageCollection) -> Image:
    """
    Generates the final tiling for the source image corresponding to
    a generated collage map.
    """
    side_count = int(len(collage_map) ** 0.5)

    tiling = Image.new(mode="RGB", size=(shape[1], shape[0]))
    sub_rows = shape[0] // side_count
    sub_cols = shape[1] // side_count

    for pos in util.progress_bar(range(len(collage_map)), name="Copying data"):
        i = collage_map[pos]
        if i == -1:
            continue

        r = pos // side_count
        c = pos % side_count

        tile = images.get_image(i)
        resized = tile.resize((sub_cols, sub_rows))
        tile.close()

        top_left = (c * sub_cols, r * sub_rows)
        tiling.paste(resized, top_left)
        resized.close()

    return tiling


def main() -> None:
    """
    Runs the entire pipeline, given images have been 'preprocessed'.
    """
    side_count = 8

    # loading the preprocessed data
    preprocessed = dict()

    if os.path.exists(config.preprocessed_file):
        with open(config.preprocessed_file) as f:
            preprocessed = {key: np.array(val) for key, val in json.load(f).items()}

    # booting up the dropbox connections
    images = dropboxManager.ImageCollection(config.dbx_access_token, config.image_path, config.local_tmp_path)
    collages = dropboxManager.ImageCollection(config.dbx_access_token, config.collage_path, config.local_tmp_path)

    targets = images.get_filenames()

    for filename in targets:
        print("Collage ("+filename+"):")
        print("Generating target...")
        image_arr = images.get_image_nparray(filename)
        target = gen_target(image_arr, side_count)
        print("Generating map...")
        collage_map = gen_map(target, preprocessed)

        # copy the data over
        tiling = gen_tiles(image_arr.shape, collage_map, images)
        numpy_collage = ((image_arr + np.array(tiling, dtype='float')) / 2).astype(np.uint8)
        collage = Image.fromarray(numpy_collage, mode='RGB')
        collages.add_image("collage_"+filename, collage)


if __name__ == "__main__":
    main()
