# -*- coding: utf-8 -*-
""" Created on Thu Jun 28 18:23:47 2018

a routine for augmentation

* checks if the frame can be extended or not
* checks the sizes of the object in the frame
* decides which extension to use
* checks xml-img couple
* proceeds the frames
* if the labels are not 'fine', they stay in the same folder unchanged
* if the labels are fine,,,but extension isn't possible it moves to fault
* if possible, new extended frames saves into same folder,and moves the originals to changed folder
  adds to changed frames "_changed"  at the end of the name
* all the changes writes in corresponding xml file
* directory of the frames is ./frames/ by default,if you don't choose manually, you must create 'frames' folder
* you can choose your own folders via command line

    !Example python processor.py --folder_name frames_folder_name
@author: Ara
"""

import random
import xml_parser
import extend_frame
from PIL import Image
import os
import shutil
import tqdm
import argparse

thresh = {'gun': {'x_thresh': 0.2, 'y_thresh': 0.2}, 'gunarm': {'x_thresh': 0.5, 'y_thresh': 0.3},
          'knife': {'x_thresh': 0.2, 'y_thresh': 0.2},
          'rifle': {'x_thresh': 0.2, 'y_thresh': 0.2}
          }

imagetypes = {'.jpg', '.png', '.jpeg'}

def random_choose_extension(arr):
    possibilities = [i for i, a in enumerate(arr) if a]
    possibilities.append(-1)
    return random.choice(possibilities)



def proceed_frame(frame, foundings):
    frame_x = frame.size[0]
    frame_y = frame.size[1]
    frame_def = dict()

    leftmost_x = -1
    rightmost_x = -1
    topmost_y = -1
    bottommost_y = -1

    for e_type, ent in foundings:
        # ent[0] represents x_min, ent[1] : y_min, ent[2] : x_max, ent[3] : y_max
        ent = [int(e) for e in ent]
        leftmost_x = ent[0] if leftmost_x < 0 else min(leftmost_x, ent[0])
        rightmost_x = ent[2] if rightmost_x < 0 else max(rightmost_x, ent[2])

        topmost_y = ent[1] if topmost_y < 0 else min(topmost_y, ent[1])
        bottommost_y = ent[3] if bottommost_y < 0 else max(bottommost_y, ent[3])
        ent_x = ent[2] - ent[0]
        ent_y = ent[3] - ent[1]
        prop_x = ent_x / frame_x
        prop_y = ent_y / frame_y

        if prop_x > thresh[e_type]['x_thresh']:
            if not frame_def.get(e_type, None):
                frame_def[e_type] = dict()

            if frame_def[e_type].get('prop_x', 0) < prop_x:
                frame_def[e_type]['prop_x'] = prop_x
                frame_def[e_type]['x_x_start'] = ent[0]
                frame_def[e_type]['x_x_end'] = ent[2]
                frame_def[e_type]['x_y_start'] = ent[1]
                frame_def[e_type]['x_y_end'] = ent[3]

        if prop_y > thresh[e_type]['y_thresh']:
            if not frame_def.get(e_type, None):
                frame_def[e_type] = dict()

            if frame_def[e_type].get('prop_y', 0) < prop_y:
                frame_def[e_type]['prop_y'] = prop_y
                frame_def[e_type]['y_x_start'] = ent[0]
                frame_def[e_type]['y_x_end'] = ent[2]
                frame_def[e_type]['y_y_start'] = ent[1]
                frame_def[e_type]['y_y_end'] = ent[3]

    x_to_extend = 0
    y_to_extend = 0
    for entity_type, deform in frame_def.items():
        if deform.get('prop_x', 0) > 0:
            x_x_to_extend = (deform.get('x_x_end') - deform.get('x_x_start')) / thresh[entity_type][
                'x_thresh'] - frame_x
            x_y_to_extend = (deform.get('x_y_end') - deform.get('x_y_start')) / thresh[entity_type][
                'y_thresh'] - frame_y
        else:
            x_x_to_extend = 0
            x_y_to_extend = 0

        if deform.get('prop_y', 0) > 0:
            y_x_to_extend = (deform.get('y_x_end') - deform.get('y_x_start')) / thresh[entity_type][
                'x_thresh'] - frame_x
            y_y_to_extend = (deform.get('y_y_end') - deform.get('y_y_start')) / thresh[entity_type][
                'y_thresh'] - frame_y
        else:
            y_x_to_extend = 0
            y_y_to_extend = 0

        x_to_extend = max(x_x_to_extend, y_x_to_extend, x_to_extend)
        y_to_extend = max(x_y_to_extend, y_y_to_extend, y_to_extend)

    left_place = leftmost_x
    right_place = frame_x - rightmost_x
    top_place = topmost_y
    bottom_place = frame_y - bottommost_y

    if left_place + right_place < x_to_extend or top_place + bottom_place < y_to_extend:
        print('no extension possible!!')
        possibility = False
    else:
        possibility = True
        # return

    extension_type = (
    ('left_extend', 'bottom_extend'), ('right_extend', 'bottom_extend'), ('left_extend', 'top_extend'),
    ('right_extend', 'top_extend'), ('both', 'both'))
    # checking if there is only one weapon,if not it will not extend

    possibilities_to_extend = [True, True, True, True]

    if left_place <= x_to_extend:
        possibilities_to_extend[0] = False
        possibilities_to_extend[2] = False
    if right_place <= x_to_extend:
        possibilities_to_extend[1] = False
        possibilities_to_extend[3] = False
    if bottom_place <= y_to_extend:
        possibilities_to_extend[0] = False
        possibilities_to_extend[1] = False
    if top_place <= y_to_extend:
        possibilities_to_extend[2] = False
        possibilities_to_extend[3] = False


    # -1 represents all directions. It is the default
    extension = -1
    if any(possibilities_to_extend):
        extension = random_choose_extension(possibilities_to_extend)
    else:
        possibility = False



    temp_y = int(x_to_extend * frame_y / frame_x)
    temp_x = int(y_to_extend * frame_x / frame_y)
    x_to_extend = int(max(x_to_extend, temp_x))
    y_to_extend = int(max(y_to_extend, temp_y))
    if extension_type[extension] == ('both', 'both'):
        x_to_extend = (left_place, right_place)
        y_to_extend = (top_place, bottom_place)


    if x_to_extend == 0 and y_to_extend == 0:
        possibility = False




    return x_to_extend, y_to_extend, extension_type[extension], possibility


def process_frames(folder, new_directory='../changed_frames'):
    if not os.path.exists('./fault/'):
        os.makedirs('./fault/')
    if not os.path.exists('./changed/'):
        os.makedirs('./changed/')
    image_types = imagetypes
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
    for filename in tqdm.tqdm(os.listdir(folder)):
        filename_, file_ext = os.path.splitext(filename)

        for imtype in image_types:
            # NOTE we assume that images are in the 'frames' folder


            imgfile = os.path.join(folder,  filename_ + imtype)


            # checks if the image exists or not with that extension
            if os.path.exists(imgfile):
                if filename.endswith(imtype):

                    img_name, img_ext = os.path.splitext(filename)

                    img_filepath = os.path.join(folder, filename )

                    # Note: name of xml and picture are the same
                    xml_filename = img_name + '.xml'
                    xml_filepath = os.path.join(folder, xml_filename)

                    weapons = xml_parser.get_information(xml_filepath)

                    frame = Image.open(img_filepath)
                    size = frame.size
                    pixel_change = [0, 0]

                    x_to_extend, y_to_extend, extend_method, is_needed = proceed_frame(frame, weapons)

                    if extend_frame.extendable(weapons):
                        if is_needed:
                            # copying to ./changed/ folder


                            new_img_filename = img_name + '_changed' + img_ext
                            new_xml_filename = img_name + '_changed' + '.xml'
                            pixel_change, new_im_size = extend_frame.extend_image(frame, x_to_extend, y_to_extend,
                                                                                  extend_method,
                                                                                  os.path.join(folder, new_img_filename),
                                                                                  weapons)

                            # new_values -> dict with keys img_filename, new_directory, width, height, depth, changes(-> representing changes in x and y of a specific pixel), new_xml_name
                            new_values = {'img_filename': new_img_filename, 'new_directory': folder,
                                          'width': (new_im_size[0]),
                                          'height': (new_im_size[1]), 'depth': 3, 'changes': pixel_change,
                                          'new_xml_name': new_xml_filename}

                            xml_parser.change_information(xml_filepath, new_values)


                            shutil.move(img_filepath, os.path.join('./changed/', filename))
                            shutil.move(xml_filepath, os.path.join('./changed/', xml_filename))
                            frame.close()
                        else:
                            frame.close()
                            new_values = {'img_filename': filename, 'new_directory': os.path.join('./fault/'),
                                          'width': (size[0]),
                                          'height': (size[1]), 'depth': 3, 'changes': pixel_change,
                                          'new_xml_name': xml_filename}
                            xml_parser.change_information(xml_filepath, new_values)
                            shutil.move(img_filepath, os.path.join('./fault/' + filename))
                            shutil.move(xml_filepath, os.path.join('./fault/' + xml_filename))





def main(args):
     process_frames(args.folder_name, args.new_folder)


if __name__ == "__main__":
    print('Starting processing')
    parser = argparse.ArgumentParser()

    parser.add_argument('--folder_name', dest='folder_name', nargs='?',
                        default='./frames/')

    parser.add_argument('--destination', dest='new_folder', nargs='?',
                        default='./output/')

    args = parser.parse_args()
    main(args)
