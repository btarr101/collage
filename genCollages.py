import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

import config
import util

def genTarget(image : np.array, sidecnt : int) -> np.array:
    '''
    Generates a target to collage for.
    '''
    cnt = sidecnt**2
    target = np.zeros(shape=(cnt, 3), dtype='float')

    rows = len(image)
    cols = len(image[0])
    subrows = rows // sidecnt
    subcols = cols // sidecnt

    for i in range(cnt):
        r = i // sidecnt
        c = i % sidecnt

        block = image[r*subrows:(r+1)*subrows,
                      c*subcols:(c+1)*subcols]
        target[i] = np.mean(block, axis=(0,1))
    return target

def genMap(target : np.array, averages : np.array) -> np.array:
    '''
    Generates a collage mapping for the target image.
    '''
    target_cnt = len(target)

    residuals = [float('inf') for i in range(target_cnt)]
    collageMap = np.full(shape=target_cnt, fill_value=-1, dtype='int32')
    image_q = list(range(len(averages)))

    while len(image_q) > 0:
        i = image_q.pop(0)
        avg = averages[i]

        best = -1
        best_residual = float('inf')

        for challenger, subtarget_avg in enumerate(target):
            challenger_residual = np.linalg.norm(subtarget_avg - avg)

            # if worse than best, skip
            if (challenger_residual > best_residual):
                continue

            # if taken, skip if I'm a worse fit
            if collageMap[challenger] != -1:
                if residuals[challenger] <= challenger_residual:
                    continue

            # update best
            best = challenger
            best_residual = challenger_residual

        # no target found
        if best == -1:
            continue

        # kick off other
        if collageMap[best] != -1:
            image_q.append(collageMap[best])

        # assign me
        collageMap[best] = i
        residuals[best] = best_residual
    return collageMap

def genTiles(shape : tuple, collageMap : np.array, data : util.ImageCollection) -> Image:
    '''
    Generates the final tiling for the source image corresponding to
    a generated collage map.
    '''
    sidecnt = int(len(collageMap) ** 0.5)

    tiling = Image.new(mode="RGB", size=(shape[1], shape[0]))
    subrows = shape[0] // sidecnt
    subcols = shape[1] // sidecnt

    for pos in util.progressBar(range(len(collageMap)), name="Copying data"):
        i = collageMap[pos]
        if i == -1:
            continue

        r = pos // sidecnt
        c = pos % sidecnt

        tile = data.GetImageFile(i)
        resized = tile.resize((subcols, subrows))
        tile.close()

        topleft = (c*subcols, r*subrows)
        tiling.paste(resized, topleft)
        resized.close()

    return tiling

def main():
    '''
    Runs the entire pipeline, given averages have been generated
    '''

    targets_indices = [10]
    sidecnt = 7

    preprocessed = np.loadtxt(config.preprocessed_file)
    data = util.ImageCollection().FromDir(config.image_dir)

    for i in targets_indices:
        print("Collage", str(i) + ":")
        print("Generating target...")
        image = data.GetData(i)
        target = genTarget(image, sidecnt)
        print(target)
        print("Generating map...")
        collageMap = genMap(target, preprocessed)
        print(collageMap)

        # copy the data over
        tiling = genTiles(image.shape, collageMap, data)
        tiling.show()

if __name__ == "__main__":
    main()

