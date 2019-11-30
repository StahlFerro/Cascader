import os
import io
import string
import shutil
import math
import time
import subprocess
import tempfile
from random import choices
from pprint import pprint
from urllib.parse import urlparse
from typing import List, Dict, Tuple
from datetime import datetime

from PIL import Image, ImageChops
from apng import APNG, PNG
from hurry.filesize import size, alternative

from .core_funcs.config import IMG_EXTS, ANIMATED_IMG_EXTS, STATIC_IMG_EXTS, ABS_CACHE_PATH, imager_exec_path
from .core_funcs.criterion import SplitCriteria
from .core_funcs.utility import _mk_temp_dir, _reduce_color, _unoptimize_gif, _log, shout_indices


def _get_gif_delay_ratios(gif_path: str, duration_sensitive: bool = False) -> List[Tuple[str, str]]:
    """ Returns a list of dual-valued tuples, first value being the frame numbers of the GIF, second being the ratio of the frame's delay to the lowest delay"""
    with Image.open(gif_path) as gif:
        indices = list(range(0, gif.n_frames))
        durations = []
        for i in indices:
            gif.seek(i)
            durations.append(gif.info['duration'])
        min_duration = min(durations)
        if duration_sensitive:
            ratios = [dur//min_duration for dur in durations]
        else:
            ratios = [1 for dur in durations]
        indexed_ratios = list(zip(indices, ratios))
    return indexed_ratios


# def _pillow_fragment_gif_frames(unop_gif_path: str, out_dir: str, criteria: SplitCriteria):
#     """ Currently UNUSED. Missing pixels """
#     gif = Image.open(unop_gif_path)
#     orig_name = os.path.splitext(os.path.basename(unop_gif_path))[0]
#     indexed_ratios = _get_gif_delay_ratios(unop_gif_path, criteria.is_duration_sensitive)
#     total_ratio = sum([ir[1] for ir in indexed_ratios])
#     sequence = 0
#     gifragment_paths = []
#     for index, ratio in indexed_ratios:
#         selector = f'"#{index}"'
#         gif.seek(index)
#         for n in range(0, ratio):
#             yield f"Splitting GIF... ({sequence + 1}/{total_ratio})"
#             save_path = os.path.join(out_dir, f'{orig_name}_{str.zfill(str(sequence), criteria.pad_count)}.png')
#             gif.save(save_path, "PNG")
#             sequence += 1


def _fragment_gif_frames(unop_gif_path: str, out_dir: str, criteria: SplitCriteria):
    """ Split GIF into separate images using Gifsicle based on the specified criteria"""
    orig_name = os.path.splitext(os.path.basename(unop_gif_path))[0]
    indexed_ratios = _get_gif_delay_ratios(unop_gif_path, criteria.is_duration_sensitive)
    total_frames = sum([ir[1] for ir in indexed_ratios])
    cumulative_index = 0
    gifragment_paths = []
    gifsicle_path = imager_exec_path('gifsicle')
    perc_skip = 5
    shout_nums = shout_indices(total_frames, perc_skip)
    for index, ratio in indexed_ratios:
        if shout_nums.get(cumulative_index):
            yield {"msg": f'Splitting frames... ({shout_nums.get(index)})'}
        selector = f'"#{index}"'
        for n in range(0, ratio):
            # yield {"msg": f"Splitting GIF... ({cumulative_index + 1}/{total_frames})"}
            save_path = os.path.join(out_dir, f'{orig_name}_{str.zfill(str(cumulative_index), criteria.pad_count)}.png')
            args = [gifsicle_path, f'"{unop_gif_path}"', selector, "--output", f'"{save_path}"']
            cmd = ' '.join(args)
            subprocess.run(cmd, shell=True)
            gifragment_paths.append(save_path)
            cumulative_index += 1
            with Image.open(save_path).convert("RGBA") as gif:
            # if gif.info.get('transparency'):
            #     yield {"msg": "Palette has transparency"}
            #     gif = gif.convert('RGBA')
            # else:
            #     yield {"msg": "Palette has no transparency"}
            #     gif = gif.convert('RGB')
                gif.save(save_path, "PNG")


def _split_gif(gif_path: str, out_dir: str, criteria: SplitCriteria):
    """ Unoptimizes GIF, and then splits the frames into separate images """
    unop_dir = _mk_temp_dir(prefix_name="unop_gif")
    color_space = criteria.color_space
    target_path = gif_path
    if color_space:
        if color_space < 2 or color_space > 256:
            raise Exception("Color space must be between 2 and 256!")
        else:
            yield {"msg": f"Reducing colors to {color_space}..."}
            target_path = _reduce_color(gif_path, unop_dir, color=color_space)
    if criteria.is_unoptimized:
        yield {"msg": f"Unoptimizing GIF..."}
        target_path = _unoptimize_gif(gif_path, unop_dir, "imagemagick")
    yield from _fragment_gif_frames(target_path, out_dir, criteria)
    # yield from _pillow_fragment_gif_frames(unop_gif_path, out_dir, criteria)
    yield {"CONTROL": "SPL_FINISH"}


def _split_apng(apng_path: str, out_dir: str, name: str, criteria: SplitCriteria):
    """ Extracts all of the frames of an animated PNG """
    img: APNG = APNG.open(apng_path)
    iframes = img.frames
    pad_count = max(len(str(len(iframes))), 3)
    fcount = len(iframes)
    perc_skip = 5
    shout_nums = shout_indices(fcount, perc_skip)
    # print('frames', [(png, control.__dict__) for (png, control) in img.frames][0])
    # with click.progressbar(iframes, empty_char=" ", fill_char="█", show_percent=True, show_pos=True) as frames:
    first_png = iframes[0][0]
    first_image = None
    with io.BytesIO() as firstbox:
        first_png.save(firstbox)
        with Image.open(firstbox) as im:
            first_image: Image = im.copy()
    yield {"MODE FIRST": first_image.mode}
    first_image = first_image.convert("RGBA")
    base_stack_image: Image = first_image.copy()
    first_size = (first_png.width, first_png.height)
    for index, (png, control) in enumerate(iframes):
        save_path = os.path.join(out_dir, f"{name}_{str.zfill(str(index), pad_count)}.png")
        if shout_nums.get(index):
            yield {"msg": f'Splitting APNG... ({shout_nums.get(index)})'}
        # if index > 0 and criteria.is_unoptimized:
        with io.BytesIO() as bytebox:
            png.save(bytebox)
            with Image.open(bytebox) as im:
                yield {"MSG": control.__dict__}
                if criteria.is_unoptimized:
                    im = im.convert("RGBA")
                    if control.depose_op == 2:
                        separate_stack = base_stack_image.copy()
                        separate_stack.paste(im, (control.x_offset, control.y_offset), im)
                        separate_stack.save(save_path)
                    else:
                        base_stack_image.paste(im, (control.x_offset, control.y_offset), im)
                        base_stack_image.save(save_path)
                else:
                    im.save(save_path)
        # else:
        #     png = png.convert("RGBA")
        #     png.save(save_path)
    yield {"CONTROL": "SPL_FINISH"}


def split_aimg(image_path: str, out_dir: str, criteria: SplitCriteria):
    """ Umbrella function for splitting animated images into individual frames """
    # print(error)
    image_path = os.path.abspath(image_path)
    if not os.path.isfile(image_path):
        raise Exception("Oi skrubman the path here seems to be a bloody directory, should've been a file", image_path)
    filename = str(os.path.basename(image_path))

    # Custom output dirname and frame names if specified on the cli
    if '.' not in filename:
        raise Exception('Where the fuk is the extension mate?!')

    name, ext = os.path.splitext(filename)
    ext = str.lower(ext[1:])
    # raise Exception(fname, ext)
    if ext not in ANIMATED_IMG_EXTS:
        raise Exception('Only supported extensions are gif and apng. Sry lad')

    out_dir = os.path.abspath(out_dir)
    if ext == 'gif':
        return _split_gif(image_path, out_dir, criteria)

    elif ext == 'png':
        return _split_apng(image_path, out_dir, name, criteria)


# if __name__ == "__main__":
#     pprint(inspect_sequence(""))

    # gs_split("./test/blobsekiro.gif", "./test/sequence/")
    # test()
    # _unoptimize_gif("./test/blobkiro.gif")
