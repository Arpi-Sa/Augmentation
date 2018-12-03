""" Created on Thu Jun 28 18:23:47 2018

Image extension

* checks if the frame can be extended or not
* checks the sizes of the object in the frame
* decides which extension to use
* if possible extends the frames
* new extended frames saves into prior created 'output' folder

@author: Ara
"""

from PIL import Image
import numpy as np
import os



weapontypes = ['gun', 'knife', 'rifle']
weaponarm = {'gunarm', 'knifearm'}

def top(im, y_to_extend):
    width, height = im.size

    subimage_box = (0, 0, width, y_to_extend)
    subimage = im.crop(subimage_box)
    subimage = subimage.transpose(Image.FLIP_TOP_BOTTOM)

    total_width = width
    total_height = y_to_extend + height

    new_im = Image.new('RGB', (total_width, total_height))
    images = [subimage, im]

    x_offset = 0
    for im in images:
        new_im.paste(im, (0, x_offset))
        x_offset += im.size[1]

    return new_im


def bottom(im, y_to_extend):
    width, height = im.size

    subimage_box = (0, height - y_to_extend - 1, width, height)
    subimage = im.crop(subimage_box)
    subimage = subimage.transpose(Image.FLIP_TOP_BOTTOM)

    total_width = width
    total_height = y_to_extend + height

    new_im = Image.new('RGB', (total_width, total_height))
    images = [im, subimage]

    x_offset = 0
    for im in images:
        new_im.paste(im, (0, x_offset))
        x_offset += im.size[1]

    return new_im


def left(im, x_to_extend):
    width, height = im.size

    subimage_box = (0, 0, x_to_extend, height)
    subimage = im.crop(subimage_box)
    subimage = subimage.transpose(Image.FLIP_LEFT_RIGHT)

    total_width = x_to_extend + width
    total_height = height

    new_im = Image.new('RGB', (total_width, total_height))
    images = [subimage, im]

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    return new_im


def right(im, x_to_extend):
    width, height = im.size

    subimage_box = (width - x_to_extend - 1, 0, width - 1, height)
    subimage = im.crop(subimage_box)
    subimage = subimage.transpose(Image.FLIP_LEFT_RIGHT)

    total_width = x_to_extend + width
    total_height = height

    new_im = Image.new('RGB', (total_width, total_height))
    images = [im, subimage]

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    return new_im


def perform_all(im, x_to_extend, y_to_extend):
    # x_to_extend represents tuple/list of x_extensions left and right
    new_im = left(im, x_to_extend[0])
    new_im = right(new_im, x_to_extend[1])
    new_im = top(new_im, y_to_extend[0])
    new_im = bottom(new_im, y_to_extend[1])

    return new_im


decision_maker = {'left_extend': left, 'right_extend': right, 'top_extend': top, 'bottom_extend': bottom,
                  'both': perform_all}

# checks whether in the image is one weapon or not
def extendable(weapons):

    #in case of 'gunarm' we assume that 'gun' and 'gunarm' stand for one weapon
    labels_without_arm = []
    for w in weapons:
        # w[0] stands for weapon
        if w[0] not in weaponarm:
            labels_without_arm.append(w[0])

    if len(labels_without_arm) > 1:
        return False
    else:
        return True

def extend_image(im, x_to_extend, y_to_extend, extension_type, name_to_save, weapons):

    ext = extendable(weapons)
    new_im = im
    if extension_type != ('both', 'both') and ext:
        # TODO: pay attention to second argument of the calls, it is highly dependent on the extension_type
        new_im = decision_maker[extension_type[0]](im, x_to_extend)
        new_im = decision_maker[extension_type[1]](new_im, y_to_extend)
    elif ext:
        new_im = perform_all(im, x_to_extend, y_to_extend)

    pixel_change = [0, 0]
    if ext:
        if extension_type[0] == 'left_extend':
            pixel_change[0] = x_to_extend
        if extension_type[1] == 'top_extend':
            pixel_change[1] = y_to_extend
        if extension_type == ('both', 'both'):
            pixel_change[0] = x_to_extend[0]
            pixel_change[1] = y_to_extend[0]

    new_im.save(name_to_save)
    return pixel_change, new_im.size

