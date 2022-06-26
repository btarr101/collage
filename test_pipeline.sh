python generate_sources.py -i images
python generate_targets.py -i images -s 9
python generate_maps.py -t images.targets -s images.sources.json
python generate_collages.py -m images.maps -c 5