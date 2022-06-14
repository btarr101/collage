import numpy as np
from PIL import Image

import config
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


def gen_map(target: np.array, averages: np.array) -> np.array:
    """
    Generates a collage mapping for the target image.
    """
    target_cnt = len(target)

    residuals = [float('inf') for i in range(target_cnt)]
    collage_map = np.full(shape=target_cnt, fill_value=-1, dtype='int32')
    image_q = list(range(len(averages)))

    while len(image_q) > 0:
        i = image_q.pop(0)
        avg = averages[i]

        best = -1
        best_residual = float('inf')

        for challenger, sub_target_avg in enumerate(target):
            challenger_residual = np.linalg.norm(sub_target_avg - avg)

            # if worse than best, skip
            if challenger_residual > best_residual:
                continue

            # if taken, skip if I'm a worse fit
            if collage_map[challenger] != -1:
                if residuals[challenger] <= challenger_residual:
                    continue

            # update best
            best = challenger
            best_residual = challenger_residual

        # no target found
        if best == -1:
            continue

        # kick off other
        if collage_map[best] != -1:
            image_q.append(collage_map[best])

        # assign me
        collage_map[best] = i
        residuals[best] = best_residual
    return collage_map


def gen_tiles(shape: tuple, collage_map: np.array, data: util.ImageCollection) -> Image:
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

        tile = data.get_image_file(i)
        resized = tile.resize((sub_cols, sub_rows))
        tile.close()

        top_left = (c * sub_cols, r * sub_rows)
        tiling.paste(resized, top_left)
        resized.close()

    return tiling


def main():
    """
    Runs the entire pipeline, given averages have been generated
    """

    targets_indices = None
    side_count = 8

    preprocessed = np.loadtxt(config.preprocessed_file)
    data = util.ImageCollection().from_dir(config.image_dir)

    targets_indices = list(range(len(data)))

    for i in targets_indices:
        print("Collage", str(i) + ":")
        print("Generating target...")
        image = data.get_image_data(i)
        target = gen_target(image, side_count)
        print(target)
        print("Generating map...")
        collage_map = gen_map(target, preprocessed)
        print(collage_map)

        # copy the data over
        tiling = gen_tiles(image.shape, collage_map, data)
        numpy_collage = ((image + np.array(tiling, dtype='float')) / 2).astype(np.uint8)
        collage = Image.fromarray(numpy_collage, mode='RGB')
        #collage.show()
        collage.save(config.collage_files(i))


if __name__ == "__main__":
    main()
