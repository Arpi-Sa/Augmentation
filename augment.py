import sys
from imgaug import augmenters as iaa
import cv2
import os
import numpy as np
import random

# Choose augmentation technique and the number of random pictures for augmentation
aug_tech_dic = {1: 'noise', 2: 'dropout', 3: 'blurr', 4: 'salt', 5: 'color'}
aug_tech = aug_tech_dic[5]
random_amount = 500


# Select random images from the original file to augment
path_origin = os.path.abspath('Scylla/scylla-engine-refactor/Data/train/images') # where the training images are
path_origin_xml = os.path.abspath('Scylla/scylla-engine-refactor/Data/train/annotations') # where the xmls are for training images
path = os.path.abspath('Augmented Data/Add_images/') # where the images for augmentation will be stored

# Tried to remove directory and makes new one
try:  
    shutil.rmtree(path)
except OSError:
    pass

os.makedirs(path)

all_data = [f for f in os.listdir(path_origin) if os.path.isfile(os.path.join(path_origin, f))] # All training images

# Copy random images to path for augmentation
for x in range(random_amount):
    if len(all_data) == 0:
        break
    else:
        file = random.choice(all_data)
        shutil.copy(os.path.join(path_origin, file), path)

# Choose augmentation technique
def choose_aug(aug):
    if aug == 'noise':
        seq = iaa.AdditiveGaussianNoise(scale=0.06*255)
    elif aug == 'dropout':
        seq = iaa.Dropout(0.02, name="Dropout")
    elif aug == 'blurr':
        seq = iaa.Sequential(iaa.GaussianBlur(sigma=(0, 3.0)))
    elif aug == 'salt':
        seq = iaa.arithmetic.CoarseSaltAndPepper(0.01, size_percent = 0.2)
    elif aug == 'color':
        seq = iaa.color.WithColorspace(to_colorspace="HSV", from_colorspace="RGB", children=iaa.WithChannels(0, iaa.Add(100)))

    path_to = os.path.abspath(f'Augmented Data/{aug}/pics') # path where the already augmented pictures are stored
    path_to_xml = os.path.abspath(f'Augmented Data/{aug}/xml') # path where the already augmented xmls are stored
    end = os.path.abspath(f'_aug_{aug}')


    return seq, path_to, path_to_xml, end


seq, path_to, path_to_xml, end = choose_aug(aug_tech) 


# Loads images, makes a list of numpy arrays, while changing the dimension of each image to [1, height, width, channel

aug_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))] # augmented images

# One by one load, augment and save
for n in aug_files:
    img = np.expand_dims(np.array(cv2.imread(os.path.join(path, n))), axis=0)
    # Initiate augmentation
    aug_img = seq.augment_images(img)
    # Rename and copy augmented images
    name, ext = os.path.splitext(n)
    cv2.imwrite(os.path.join(path_to, name + end + ext), np.squeeze(aug_img, axis = 0))
    # copy xmls to path
    name, ext = os.path.splitext(n)
    shutil.copy(os.path.join(path_origin_xml, name + '.xml'), path_to_xml)
print('Done renaming augmented files')


# Rename XML files
aug_files_xml = [ f for f in os.listdir(path_to_xml) if os.path.isfile(os.path.join(path_to_xml,f)) ]

for f in aug_files_xml:
    name, ext = os.path.splitext(f)
    os.rename(os.path.join(path_to_xml, f), os.path.join(path_to_xml, name + end + ext))


