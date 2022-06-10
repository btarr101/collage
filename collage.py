import os
import numpy as np
from matplotlib import pyplot as plt
from skimage.transform import resize

from ImageCollection import ImageCollection

image_dir = './Images'
target_idx = 20

if __name__ == '__main__':
    img_data = ImageCollection().FromDir(image_dir)

    # number of images representing the collage
    image_count = len(img_data)
    side_count = int(np.floor((image_count -1) ** 0.5))
    sub_images = side_count ** 2

    # the target of the collage
    target_image = img_data.GetData(target_idx)
    sub_targets = np.zeros(shape=(side_count, side_count, 3), dtype='float')

    img_rows = len(target_image)
    img_cols = len(target_image[0])

    sub_rows = int(img_rows / side_count)
    sub_cols = int(img_cols / side_count)

    # Calculating the sub targets
    for r, row in enumerate(sub_targets):
        for c, color in enumerate(row):
            block = target_image[r*sub_rows:(r+1)*sub_rows,
                                 c*sub_cols:(c+1)*sub_cols]
            avg = np.int32(np.average(np.average(block, axis=0), axis=0))
            sub_targets[r, c] = avg

    # Calculating average color for the available pool
    averages = []
    for i in range(0, len(img_data)):
        data = img_data.GetData(i)

        avg = np.average(np.average(data, axis=0), axis=0)
        averages.append(avg)

        print("--")
        print("Image ", i)
        print("Average color=", averages[i])
        print("--")

    # ===== MATH IMPL HERE ==========
    final_indices = np.zeros(shape=(side_count, side_count), dtype='int32')

    for r, row in enumerate(sub_targets):
        for c, actual in enumerate(row):
            print("r: ", r, ", c: ", c)

            nearest_sofar = 0
            nearest_dist = np.linalg.norm(averages[nearest_sofar] - actual)

            for test, avg in enumerate(averages):
                test_dist = np.linalg.norm(avg - actual)
                if (test_dist < nearest_dist):
                    nearest_sofar = test

            final_indices[r,c] = nearest_sofar
            averages[nearest_sofar] = np.zeros(3)
    # ===== END MATH IMPL ===========

    # Aligning the subimages to produce the final image
    final_image = np.zeros(shape=(img_rows, img_cols, 3), dtype='int32')

    for r, row in enumerate(final_indices):
        for c, i in enumerate(row):
            print("iter: ", r*side_count +c)
            final_image[r*sub_rows:(r+1)*sub_rows,
                        c*sub_cols:(c+1)*sub_cols] = img_data.GetData(i)[::side_count,::side_count]
    plt.imshow(final_image)
    plt.show()
