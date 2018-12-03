""" Created on Thu Jun 28 18:23:47 2018

Working with corresponding xml files


* checks xml-img couple
* gets the information from xml file
* all the changes writes in corresponding xml file
* adds to processed frames "_processed" at the end of name


@author: Ara
"""

import xml.etree.ElementTree as ET
import os


def get_wanting_tag(parent, child_name):
    children = []
    for child in parent:
        if child.tag == child_name:
            children.append(child)

    return children


def get_information(filename):
    weapons = []
    tree = ET.parse(filename)
    root = tree.getroot()
    objects = get_wanting_tag(root, 'object')
    for o in objects:
        name = ''
        bndbox = ()
        for info in o:
            if info.tag == 'name':
                name = info.text
            elif info.tag == 'bndbox':
                bndbox = tuple([c.text for c in info])
        weapons.append((name, bndbox))
    return weapons


# values represent x_change and y_change respectively
def handle_object_change(obj, values):
    bndbox = obj[4]
    if bndbox.tag == 'bndbox':
        for i, s in enumerate(bndbox):
            s.text = str(int(s.text) + values[int(i % 2)])
    else:
        print('Something has changed in xml!!')
    return obj


# new_name -> dict with keys img_filename, new_directory, width, height, depth, changes(-> representing changes in x and y of a specific pixel), new_xml_name
def change_information(filename, new_values):

    tree = ET.parse(filename)
    root = tree.getroot()


    for child in root:
        if child.tag == 'filename':
            child.text = new_values['img_filename']
        elif child.tag == 'folder':
            child.text = os.path.basename(os.path.normpath(new_values['new_directory']))
        elif child.tag == 'path':
            child.text = os.path.abspath(os.path.join(new_values['new_directory'], new_values['img_filename']))
        elif child.tag == 'size':
            for s in child:
                s.text = str(new_values[s.tag])
        elif child.tag == 'object' and any(new_values['changes']):
            child = handle_object_change(child, new_values['changes'])


    tree.write(os.path.join(new_values['new_directory'], new_values['new_xml_name']))


