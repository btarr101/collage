#!/usr/bin/env bash

# Checks if the previous python script failed, and if so
# stops the pipeline.
function check_exitcode {
  if [ $? -eq 1 ]; then
    echo
    echo Stopping pipeline...
    exit 1
  fi
}

# Make a tmp directory for all these files
export SRC=$PWD
export BIN=./bin
mkdir "$BIN" -p
cd "$BIN" || exit

# 2) Fetch images
echo
python "$SRC/dropbox_fetcher.py" -t "$DBX_TOKEN" -r "/images" -l "images"
check_exitcode

# 1) Generate sources
echo
python "$SRC/generate_sources.py" -i "images"
check_exitcode

# 2) Generate targets
echo
python "$SRC/generate_targets.py" -i "images" -s 9
check_exitcode

# 3) Generate maps
echo
python "$SRC/generate_maps.py" -t "images.targets" -s "images.sources.json"
check_exitcode

# 4) Generate final collages
echo
python "$SRC/generate_collages.py" -m "images.maps" -c 5
check_exitcode
