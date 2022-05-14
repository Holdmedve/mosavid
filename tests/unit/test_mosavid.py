from plistlib import InvalidFileException
import pytest
import cv2
import numpy as np

from project.mosavid import (
    get_frames_from_video,
    split_image_into_tiles,
    mean_color_euclidian_distance,
    stitch,
)
from project.exceptions import InvalidSplitLevel

from project.helpers import get_even_samples, is_data_valid, Data

from tests.utils import *


class TestStitchTiles:
    def test__when_called_with_4_pixels_as_tiles__returns_them_as_1_array(self):
        tiles = [
            [black_img(), white_img()],
            [white_img(), black_img()],
        ]
        expected_image = np.array(
            [[BLACK_PIXEL, WHITE_PIXEL], [WHITE_PIXEL, BLACK_PIXEL]]
        )

        image = stitch(tiles)

        assert (image == expected_image).all()


class TestMeanColorEuclidianDistance:
    def test__when_called_with_same_image__returns_1(self):
        img = cv2.imread(TEST_JPG_PATH)

        dst = mean_color_euclidian_distance(img, img)

        assert dst == 0.0

    def test__when_called_with_black_and_white_pixels__returns_body_diagonal_of_cube_with_255_long_edges(
        self,
    ):
        # return value of tested function is rounded differently hence the use of str
        expected_dst = 255 * np.sqrt(3)
        expected_dst = str(expected_dst)

        dst = mean_color_euclidian_distance(black_img(), white_img())
        dst = str(dst)

        assert dst[: len(dst) - 1] == expected_dst[: len(expected_dst) - 2]

    def test__order_of_inputs_does_not_influence_result(self):
        result_1 = mean_color_euclidian_distance(BLACK_IMG, WHITE_IMG)
        result_2 = mean_color_euclidian_distance(WHITE_IMG, BLACK_IMG)

        assert result_1 == result_2


class TestGetFramesFromVideo:
    def test__when_called_with_test_mp4__returns_right_number_of_frames(self):
        frames = get_frames_from_video(TEST_MP4_PATH)
        assert len(frames) == 145


class TestSplitImageIntoTiles:
    @pytest.mark.parametrize(
        "split_level, expected_tile_dimensions", [(1, (2, 2)), (3, (8, 8))]
    )
    def test__when_called_with_certain_split_level__returns_tiles_in_excpected_dimensions(
        self, split_level, expected_tile_dimensions
    ):
        tiles = split_image_into_tiles(TEST_JPG_PATH, split_level)

        assert len(tiles) == expected_tile_dimensions[0]
        assert len(tiles[0]) == expected_tile_dimensions[1]
        assert len({len(row) for row in tiles}) == 1


class TestSplitInteger:
    @pytest.mark.parametrize(
        "to_split, split_degree, expected_splits",
        [
            (300, 4, (0, 100, 200, 300)),
            (1452, 8, (0, 207, 414, 622, 829, 1037, 1244, 1452)),
        ],
    )
    def test__when_called__returns_expected_splits(
        self, to_split, split_degree, expected_splits
    ):
        splits = get_even_samples(to_split, split_degree)

        assert splits == expected_splits


@pytest.mark.parametrize(
    "invalid_data, expected_exception",
    [
        (
            Data(
                target_image_path="invalid_image_path",
                source_video_path=TEST_MP4_PATH,
                requested_split_level=1,
            ),
            FileNotFoundError,
        ),
        (
            Data(
                target_image_path=TEST_JPG_PATH,
                source_video_path="invalid_video_path",
                requested_split_level=1,
            ),
            FileNotFoundError,
        ),
        (
            Data(
                target_image_path=TEST_JPG_PATH,
                source_video_path=TEST_MP4_PATH,
                requested_split_level=0,
            ),
            InvalidSplitLevel,
        ),
    ],
)
def test__is_data_valid__invalid_property__raises_expected_exception(
    invalid_data, expected_exception
):
    with pytest.raises(expected_exception=expected_exception):
        is_data_valid(data=invalid_data)
