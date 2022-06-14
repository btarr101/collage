import os
import numpy as np

# data directories/files
data_dir = os.path.join(".", "data")
image_dir = os.path.join(data_dir, "images")
collage_dir = os.path.join(data_dir, "collages")

preprocessed_file = os.path.join(data_dir, "preprocessed.txt")
collage_files = lambda i : os.path.join(collage_dir, str(i)+".jpg")

