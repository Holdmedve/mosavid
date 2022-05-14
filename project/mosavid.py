import numpy as np

from dataclasses import dataclass
from numpy import ndarray
from typing import Callable
from project.distance import mean_color_euclidian_distance

from project.helpers import get_frames_from_video, split_image_into_tiles


@dataclass
class Config:
    split_level: int
    comparison_method: Callable[[ndarray, ndarray], float]


def stitch(images: list[list[ndarray]]) -> ndarray:
    result: ndarray

    for x in range(len(images)):
        row: ndarray
        for y in range(len(images[0])):
            if y == 0:
                row = images[x][y]
            else:
                row = np.concatenate((row, images[x][y]), axis=1)
        if x == 0:
            result = row
        else:
            result = np.concatenate((result, row), axis=0)

    return result


def find_best_fitting_frame(
    frames: list[ndarray],
    tile: ndarray,
    comparison_fn: Callable[[ndarray, ndarray], float],
) -> ndarray:
    best_fit: ndarray = frames[0]
    best_dst: float = float("inf")

    for f in frames:
        dst = comparison_fn(f, tile)
        if dst < best_dst:
            best_fit = f
            best_dst = dst

    return best_fit


def get_best_fitting_frames(
    target_tiles: list[list[ndarray]],
    frames,
    comparison_fn: Callable[[ndarray, ndarray], float],
) -> list[list[ndarray]]:
    best_fitting_frames: list[list[ndarray]]

    for x in range(len(target_tiles)):
        row: list[ndarray]
        for y in range(len(target_tiles[0])):
            f = find_best_fitting_frame(frames, target_tiles[x][y], comparison_fn)
            if y == 0:
                row = [f]
            else:
                row.append(f)
        if x == 0:
            best_fitting_frames = [row]
        else:
            best_fitting_frames.append(row)

    return best_fitting_frames


def create_mosaic_from_video(target_img_path: str, source_video_path: str) -> ndarray:
    target_tiles: list[list[ndarray]] = split_image_into_tiles(target_img_path, 2)
    frames: list[ndarray] = get_frames_from_video(source_video_path)

    best_fitting_frames: list[list[ndarray]] = get_best_fitting_frames(
        target_tiles, frames, mean_color_euclidian_distance
    )

    result: ndarray = stitch(best_fitting_frames)

    return result
