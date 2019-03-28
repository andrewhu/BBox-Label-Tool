from PIL import Image
import os
from tqdm import tqdm

THUMBNAIL_FOLDER = "Thumbnails"


ignore = ["examples", "_trash"] # Folders to ignore

folders = [x for x in os.listdir("Images") if x not in ignore]

# Create folders
if not os.path.exists(THUMBNAIL_FOLDER):
    os.mkdir(THUMBNAIL_FOLDER)

categories = open("classes.txt").read().splitlines()
for category in categories:
    if not os.path.exists(os.path.join(THUMBNAIL_FOLDER, category)):
        os.mkdir(os.path.join(THUMBNAIL_FOLDER, category))

for folder in folders:
    #if not os.path.exists(os.path.join("Thumbnails", folder)):
    #    os.mkdir(os.path.join("Thumbnails", folder))
    print("Now creating thumbnails from '%s'" % folder)
    images = os.listdir(os.path.join("./Images", folder))
    labels = [x[:-4]+".txt" for x in images]
    for image, label in tqdm(zip(images, labels), total=len(images)):
        im_path = os.path.join("Images", folder, image)
        im = Image.open(im_path).convert('RGB')
        coords = open(os.path.join("Labels", folder, label)).read().splitlines()
        for i, coord in enumerate(coords):
            coord = coord.split()
            crop_region = tuple(map(int, coord[:4]))
            category = coord[6]
            im.crop(crop_region).save(os.path.join(THUMBNAIL_FOLDER, category, image[:-4]+'-'+str(i)+'.jpg'))
            #print(crop_region, category)
            
