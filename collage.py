import os
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

from ImageCollection import ImageCollection

MAX_RES = 442 # sqrt(255^2 + 255^2 + 255^2)

image_dir = './Images'
target_idx = 35

if __name__ == '__main__':
    img_data = ImageCollection(maxSize=10).FromDir(image_dir)

    # number of images representing the collage
    image_count = len(img_data)
    side_count = int(np.floor((image_count -1) ** 0.5))
    sub_images = side_count ** 2

    for target_i in range(image_count):
        print("target=", target_i)

        # the target of the collage
        target_image = img_data.GetData(target_i)
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

            print(i, " average=", averages[i])

        # ===== MATH IMPL HERE ==========
        residuals = [-1.0 for i in range(len(averages))]
        assignments = np.full(shape=(side_count, side_count), fill_value=-1, dtype='int32') # current image assignments
        queue = list(range(len(averages))) # queue of available images

        while len(queue) > 0:
            i = queue.pop(0)
            avg = averages[i]
            print("i=", i)

            best_target = (-1, -1)
            best_target_res = MAX_RES

            for r, row in enumerate(sub_targets):
                for c, actual in enumerate(row):
                    maybe_better_res = np.linalg.norm(sub_targets[r, c] - avg)
                    if maybe_better_res < best_target_res:

                        # If the position is already assigned
                        assigned = assignments[r, c]
                        if assigned != -1:
                            assigned_res = residuals[assigned]

                            # if the new assignment isn't better than the current one, cancel this as
                            # an option
                            if (residuals[assigned] <= maybe_better_res):
                                continue

                        best_target_res = maybe_better_res
                        best_target = (r, c)

            # assign this image
            if best_target != (-1, -1):

                # kick off an assigned if it should be, and put it back on queue
                assigned = assignments[best_target[0], best_target[1]]
                if assigned != -1:
                    print("kicked off ", assigned, " from ", best_target)
                    queue.append(assigned)

                assignments[best_target[0], best_target[1]] = i
                residuals[i] = best_target_res
                print("assigned ", i, " to ", best_target)

        '''
        for r, row in enumerate(sub_targets):
            for c, actual in enumerate(row):
                print("r: ", r, ", c: ", c)

                nearest_sofar = 0
                nearest_dist = np.linalg.norm(averages[nearest_sofar] - actual)

                for test, avg in enumerate(averages):
                    test_dist = np.linalg.norm(avg - actual)
                    if (test_dist < nearest_dist):
                        nearest_sofar = test
                        nearest_dist = test_dist

                assignments[r,c] = nearest_sofar
                #averages[nearest_sofar] = np.zeros(3)
        '''
        # ===== END MATH IMPL ===========

        # Aligning the subimages to produce the final image
        final_image = np.zeros(shape=(img_rows, img_cols, 3), dtype='int32')
        map_image = sub_targets.astype(int)

        for r, row in enumerate(assignments):
            for c, i in enumerate(row):
                if i == -1:
                    continue
                print("r, c: [",r,", ",c,"]")
                final_image[r*sub_rows:(r+1)*sub_rows,
                            c*sub_cols:(c+1)*sub_cols] = img_data.GetData(i)[::side_count,::side_count]

        tosave = ((final_image + target_image) // 2).astype(np.uint8)
        im = Image.fromarray(tosave)
        im.save(str(target_i)+".jpg")
