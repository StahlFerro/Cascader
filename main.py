from __future__ import print_function
import sys
import random
import string
from typing import List

import zerorpc

from pybrain.inspect_ops import _inspect_aimg, _inspect_sequence
from pybrain.aimg_ops import split_aimg, create_aimg, _delete_temp_images
from pybrain.sprite_ops import _build_spritesheet
from pybrain.config import CreationCriteria, SplitCriteria, SpritesheetBuildCriteria, SpritesheetSliceCriteria

class API(object):

    def inspect_aimg(self, image_path):
        info = _inspect_aimg(image_path)
        return info

    def inspect_sequence(self, dir_path):
        info = _inspect_sequence(dir_path)
        return info

    def combine_image(self, image_paths, out_dir, filename, fps, extension, width, height, reverse, transparent, flip_h, flip_v):
        # raise Exception(image_paths, out_dir, filename, fps, extension, fps, reverse, transparent)
        if not image_paths and not out_dir:
            raise Exception("Please load the images and choose the output folder!")
        elif not image_paths:
            raise Exception("Please load the images!")
        elif not out_dir:
            raise Exception("Please choose the output folder!")
        criteria = CreationCriteria(fps, extension, reverse, transparent).transform(width, height, flip_h, flip_v)
        res = create_aimg(image_paths, out_dir, filename, criteria)
        return res

    def split_image(self, image_path, out_dir, pad_count, is_duration_sensitive):
        if not image_path and not out_dir:
            raise Exception("Please load a GIF or APNG and choose the output folder!")
        elif not image_path:
            raise Exception("Please load a GIF or APNG!")
        elif not out_dir:
            raise Exception("Please choose an output folder!")
        criteria = SplitCriteria(pad_count, is_duration_sensitive)
        res = split_aimg(image_path, out_dir, criteria)
        return res

    def delete_temp_images(self):
        res = _delete_temp_images()
        return res

    def build_spritesheet(self, image_paths, input_mode, out_dir, filename, width, height, tiles_per_row, off_x, off_y, pad_x, pad_y, preserve_alpha):
        if not image_paths and not out_dir:
            raise Exception("Please load the images and choose the output folder!")
        elif not image_paths:
            raise Exception("Please load the images!")
        elif not out_dir:
            raise Exception("Please choose the output folder!")
        criteria = SpritesheetBuildCriteria(width, height, tiles_per_row, off_x, off_y, pad_x, pad_y, preserve_alpha)
        # raise Exception(criteria.__dict__)
        _build_spritesheet(image_paths, input_mode, out_dir, filename, criteria)


def parse_port():
    return 4242


def main():
    address = f"tcp://127.0.0.1:{parse_port()}"
    server = zerorpc.Server(API())
    server.bind(address)
    print(f"Start running on {address}")
    print(server.run())


if __name__ == "__main__":
    main()
