import json
from pathlib import Path

import numpy as np
from defopt import run
from progressbar import progressbar


def create_array(target: np.ndarray, sources: dict[str, np.ndarray]) -> tuple[np.ndarray, float]:
    """
    Creates an array that represents a mapping from sources to a target,
    essentially this is where the actual math behind generating the collage is.

    :param target: the target colors of an image.
    :param sources: the dictionary of sources for the images.
    :return: a tuple of a numpy array (matrix) of paths to the appropriate images, and the
             sum of squares of the residuals as the second element.
    """

    mapping = np.array(
        [["none" for _ in range(target.shape[0])] for _ in range(target.shape[1])],
        dtype=object
    )

    residuals = np.full(mapping.shape, float('inf'), dtype=np.float64)

    # create a queue of sources that still need to be assessed
    source_q = list(sources.keys())

    # assess the sources
    while len(source_q) > 0:
        source_path = source_q.pop(0)
        source_color = sources[source_path]

        best_loc = (-1, -1)
        best_residual = float('inf')

        # iterate through each position and calculate the residual between that position's
        # color and the average color of the source.
        for r, row in enumerate(target):
            for c, color in enumerate(row):
                residual = np.linalg.norm(color - source_color)

                # if worse than best, skip
                if residual > best_residual:
                    continue

                # if taken, skip if I'm a worse fit
                if residuals[r, c] <= residual:
                    continue

                # this is a potential option
                best_loc = (r, c)
                best_residual = residual

        # no slot found
        if best_loc == (-1, -1):
            continue

        # if another source is occupying the slot I want, kick that source
        # back onto the queue, so I can take the slot
        if mapping[best_loc] != "none":
            source_q.append(mapping[best_loc])

        # assign me to my desired slot
        mapping[best_loc] = source_path
        residuals[best_loc] = best_residual

    sos = sum(res**2 for res in np.nditer(residuals)) ** 0.5
    return mapping, sos


def main(*, target_or_target_dir: Path, sources_path: Path) -> None:
    """
    Generates mapping files for target(s) and sources. If a directory is specified
    for TARGET_OR_TARGET_DIR then a directory of mappings will be generated,
    otherwise a single map will be generated.

    :param target_or_target_dir: the directory of targets to generate mapping(s) from.
    :param sources_path: the json of sources for the images.
    """

    if target_or_target_dir.is_dir():
        target_paths = list(target_or_target_dir.glob('*'))
        out_dir = target_or_target_dir.with_name(target_or_target_dir.name[:-len('.targets')] + '.maps')
        if not out_dir.exists():
            out_dir.mkdir(exist_ok=False)
    else:
        target_paths = [target_or_target_dir]
        out_dir = Path('.')

    print(f"Generating from {target_or_target_dir}:")
    for target_path in progressbar(target_paths):

        with np.load(target_path) as npz:
            target = npz['arr']  # load target
            label = npz['label']  # load label

        with open(sources_path) as f:  # load sources
            sources = {key: np.array(val, dtype=np.float64) for key, val in json.load(f).items()}

        arr, sos = create_array(target, sources)
        np.savez(out_dir / (target_path.name[:-len('.target.npz')] + '.map.npz'),
                 arr=arr,
                 label=label,
                 sos=sos,
                 allow_pickle=True)
    print(f"\t-> Outputted to {out_dir if len(target_paths) > 1 else target_paths[0]}")


if __name__ == "__main__":
    run(main)
