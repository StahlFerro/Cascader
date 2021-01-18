from __future__ import print_function
import sys
import random
import string
from typing import List
import os
import signal
import time
import json

from pycore.inspect_ops import inspect_sequence, inspect_general, _inspect_smart
from pycore.create_ops import create_aimg
from pycore.split_ops import split_aimg
from pycore.sprite_ops import _build_spritesheet, _slice_spritesheet
from pycore.modify_ops import modify_aimg
from pycore.core_funcs.criterion import CriteriaBundle, CreationCriteria, SplitCriteria, ModificationCriteria, SpritesheetBuildCriteria, SpritesheetSliceCriteria, GIFOptimizationCriteria, APNGOptimizationCriteria
from pycore.core_funcs.utility import _purge_directory, util_generator, util_generator_shallow
from pycore.core_funcs.config import ABS_CACHE_PATH, ABS_TEMP_PATH, get_bufferfile_content, get_criterionfile_content


IS_FROZEN = getattr(sys, 'frozen', False)

class PythonImager():

    def echo(self, msg):
        print(msg)
        return f"{msg} echoed"


    def echostream(self, stdin_data):
        print(type(stdin_data))
        if type(stdin_data) != str:
            print(stdin_data.read())
        else:
            print(stdin_data)


    def inspect_one(self, image_path, filter=""):
        """Inspect a single image and then return its information"""
        info = inspect_general(image_path, filter)
        if (info):
            info = json.dumps({"data": info})
            print(info)


    def inspect_many(self, image_paths: List):
        """ Inspect a sequence of images and then return their information.
            Intermediary buffer file is used to avoid char limit of command lines
        """
        info = inspect_sequence(image_paths)
        if (info):
            info = json.dumps({"data": info})
            print(info)


    def inspect_smart(self, image_path):
        """Inspect a sequence of images and then return their information"""
        info = _inspect_smart(image_path)
        if (info):
            info = json.dumps({"data": info})
            print(info)


    def combine_image(self, out_dir, filename):
        """Combine multiple static images into a single animated image file"""
        image_paths = get_bufferfile_content()
        criterion_vals = get_criterionfile_content()
        """Combine a sequence of images into a GIF/APNG"""
        # raise Exception(image_paths, out_dir, filename, fps, extension, fps, reverse, transparent)
        if not image_paths and not out_dir:
            raise Exception("Please load the images and choose the output folder!")
        elif not image_paths:   
            raise Exception("Please load the images!")
        elif not out_dir:
            raise Exception("Please choose the output folder!")
        crbundle = CriteriaBundle({
            "create_aimg": CreationCriteria(criterion_vals),
            "gif_opt": GIFOptimizationCriteria(criterion_vals),
            "apng_opt": APNGOptimizationCriteria(criterion_vals)
        })
        out_path = create_aimg(image_paths, out_dir, filename, crbundle)
        if (out_path):
            print(json.dumps({"data": out_path}))
        return


    def split_image(self, image_path, out_dir, vals):
        """Split all the frames of a GIF/APNG into a sequence of images"""
        if not image_path and not out_dir:
            raise Exception("Please load a GIF or APNG and choose the output folder!")
        elif not image_path:
            raise Exception("Please load a GIF or APNG!")
        elif not out_dir:
            raise Exception("Please choose an output folder!")
        criteria = SplitCriteria(vals)
        return split_aimg(image_path, out_dir, criteria)


    def modify_image(self, image_path, out_dir, vals):
        """Modify the criteria and behavior of a GIF/APNG"""
        if not image_path and not out_dir:
            raise Exception("Please load a GIF or APNG and choose the output folder!")
        elif not image_path:
            raise Exception("Please load a GIF or APNG!")
        elif not out_dir:
            raise Exception("Please choose an output folder!")
        criteria = ModificationCriteria(vals)
        crbundle = CriteriaBundle({
            'modify_aimg': ModificationCriteria(vals),
            'gif_opt': GIFOptimizationCriteria(vals),
            'apng_opt': APNGOptimizationCriteria(vals),
        })
        return modify_aimg(image_path, out_dir, crbundle)
        

    def build_spritesheet(self, image_paths, out_dir, filename, vals: dict):
        """Build a spritesheet using the specified sequence of images"""
    # def build_spritesheet(self, image_paths, input_mode, out_dir, filename, width, height, tiles_per_row, off_x, off_y, pad_x, pad_y, preserve_alpha):
        if not image_paths and not out_dir:
            raise Exception("Please load the images and choose the output folder!")
        elif not image_paths:
            raise Exception("Please load the images!")
        elif not out_dir:
            raise Exception("Please choose the output folder!")
        criteria = SpritesheetBuildCriteria(vals)
        # raise Exception(criteria.__dict__)
        # yield {"msg": "yo"}
        return _build_spritesheet(image_paths, out_dir, filename, criteria)


    def slice_spritesheet(self, image_path, out_dir, filename, vals: dict):
        """Slice a spritesheet into individual sections"""
        if not image_path and not out_dir:
            raise Exception("Please load the spritesheet and choose the output folder!")
        elif not image_path:
            raise Exception("Please load the spritesheet!")
        elif not out_dir:
            raise Exception("Please choos the output folder")
        criteria = SpritesheetSliceCriteria(vals)
        return _slice_spritesheet(image_path, out_dir, filename, criteria)


    def purge_cache_temp(self):
        """Remove cache and temp directories"""
        _purge_directory(ABS_TEMP_PATH())
        _purge_directory(ABS_CACHE_PATH())
        return "Cache and temp evaporated"


    def print_cwd(self):
        """Dev method for displaying python cwd"""
        msg = {
            "os.getcwd()": os.getcwd(),
            "sys.executable": sys.executable,
            "__file__": __file__,
            "IS_FROZEN": IS_FROZEN
        }
        return msg


    def test_generator(self):
        return util_generator()



def handle_execpath():
    if IS_FROZEN:
        frozen_dir = os.path.dirname(sys.executable)
        os.chdir(frozen_dir)


def main():
    if len(sys.argv) == 1 and not sys.stdin.isatty():
        try:
            data = json.loads(sys.stdin.read())
        except Exception as e:
            print(e)
        pyimager = PythonImager()   
        try:
            method = getattr(pyimager, data['command'])
        except AttributeError:
            raise NotImplementedError(f"Method {data['command']} not implemented")
        args = data['args']
        method(*args)


if __name__ == "__main__":
    main()
