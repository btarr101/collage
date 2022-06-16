import os

# local data
# these are directories used for caching data processed or directly downloaded
# from the dropbox
local_tmp_path = os.path.join(".", "tmp")
preprocessed_file = os.path.join(local_tmp_path, "preprocessed.json")

# dropbox
# these are directories made in the dropbox
image_path = "/IMAGE_PATH"
collage_path = "/COLLAGE_PATH"

# Sensitive below
dbx_access_token = 'YOUR TOKEN HERE'
