import os
import string
import math
from random import choices
from pprint import pprint
from urllib.parse import urlparse

from PIL import Image
from apng import APNG
from colorama import init, deinit
from hurry.filesize import size, alternative

from .config import IMG_EXTS, STATIC_IMG_EXTS, ANIMATED_IMG_EXTS


def _inspect_image(animage_path):
    """Returns information of an animted GIF/APNG"""
    abspath = os.path.abspath(animage_path)
    filename = str(os.path.basename(abspath))
    ext = str.lower(os.path.splitext(filename)[1])

    frame_count = 0
    fps = 0
    avg_delay = 0
    fsize = size(os.stat(abspath).st_size, system=alternative)
    # fsize = 0
    width = height = 0
    loop_duration = 0
    extension = ''
    uneven_delay = False

    if ext == '.gif':
        try:
            gif: Image = Image.open(abspath)
        except Exception:
            raise Exception(f'The chosen file ({filename}) is not a valid GIF image')
        if gif.format != 'GIF' or not gif.is_animated:
            raise Exception(f"The chosen GIF ({filename}) is not an animated GIF!")
        width, height = gif.size
        frame_count = gif.n_frames
        # pprint(gif.info)
        delays = []
        for f in range(0, gif.n_frames):
            gif.seek(f)
            delays.append(gif.info['duration'])
        
        # raise Exception(delays)
        uneven_delay = len(set(delays)) > 1
        avg_delay = sum(delays) / len(delays)
        fps = round(1000.0 / avg_delay, 3)
        loop_duration = round(frame_count / fps, 3)
        extension = 'GIF'

    elif ext == '.png':
        try:
            apng: APNG = APNG.open(abspath)
        except Exception:
            raise Exception(f'The chosen file ({filename}) is not a valid PNG image')
        frames = apng.frames
        frame_count = len(frames)
        if frame_count <= 1:
            raise Exception(f"The chosen PNG ({filename}) is not an animated PNG!")
        png_one, controller_one = frames[0]
        # pprint(png_one.__dict__)
        # pprint(controller_one.__dict__)
        extension = 'APNG'
        width = png_one.width
        height = png_one.height
        delays = [f[1].delay for f in frames]
        avg_delay = sum(delays) / frame_count
        uneven_delay = len(set(delays)) > 1
        fps = round(1000.0 / avg_delay, 3)
        loop_duration = round(frame_count / fps, 3)

    image_info = {
        "name": filename,
        "fps": fps,
        "avg_delay": round(avg_delay / 1000, 3),
        "uneven_delay": uneven_delay,
        "fsize": fsize,
        "extension": extension,
        "frame_count": frame_count,
        "absolute_url": abspath,
        "width": width,
        "height": height,
        "loop_duration": loop_duration,
    }
    return image_info


def _inspect_sequence(image_paths):
    """Returns information of a selected sequence of images"""
    abs_image_paths = [os.path.abspath(ip) for ip in image_paths if os.path.exists(ip)]
    img_paths = [f for f in abs_image_paths if str.lower(os.path.splitext(f)[1][1:]) in STATIC_IMG_EXTS]
    # raise Exception("imgs", imgs)
    print("imgs count", len(img_paths))
    # pprint(imgs)
    if not img_paths:
        raise Exception("No images selected. Make sure the path to them are correct and they are static images")
    first_img_name = os.path.splitext(img_paths[0])[0]
    filename = os.path.basename(first_img_name.split('_')[0] if '_' in first_img_name else first_img_name)
    # apngs = [apng for apng in (APNG.open(i) for i in imgs) if len(apng.frames) > 1]
    # gifs = [gif for gif in (Image.open(i) for i in imgs) if gif.format == "GIF" and gif.is_animated]
    sequence = [i for i in img_paths if len(APNG.open(i).frames) == 1 and Image.open(i).format != "GIF"]
    sequence_count = len(sequence)
    sequence_filesize = size(sum([os.stat(i).st_size for i in sequence]), system=alternative)
    print("statics count", sequence_count)
    if not sequence:
        raise Exception("The images choosen must be static images, not animted GIFs or PNGs!")
    width, height = Image.open(sequence[0]).size
    # pprint(apngs)
    # pprint(gifs)
    # if any(APNG.open(i) for i in imgs)):

    sequence_info = {
        "name": filename,
        "total": sequence_count,
        "sequence": sequence,
        "size": sequence_filesize,
        "width": width,
        "height": height,
    }
    return sequence_info
