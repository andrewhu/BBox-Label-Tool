#-------------------------------------------------------------------------------
# Name:        Bounding Box to YOLO Conversion script
# Purpose:     Converts bounding box labels from <x1, y1, x2, y2, w, h> format 
#               to <x_ratio, y_ratio, w_ratio, h_ratio> for YOLO training
# Author:      Andrew Hu
# Created:     03/12/2019
#
#-------------------------------------------------------------------------------


from PIL import Image
import os

OUTPUT_DIR = "YOLO_Formatted"

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
folders = os.listdir("Images")

# only convert labels from the images we keep
label_files = [x[:-4]+".txt" for x in os.listdir(IMAGE_PATH)]

with open("classes.txt") as f:
    classes = [x.strip() for x in f.readlines()]
print("Classes:", classes)

for label_file in label_files:
    with open(os.path.join(LABEL_PATH, label_file)) as input_file:
        labels = [x.strip() for x in input_file.readlines()]
    formatted_file = open(os.path.join(OUTPUT_DIR, label_file), "w")
    for label in labels:
        label = label.split()
        x1, y1, x2, y2, w, h = tuple([int(i) for i in label[:-1]])
        center_x = float(x1+x2)/2
        center_y = float(y1+y2)/2
        center_x_f = float(center_x)/int(w)
        center_y_f = float(center_y)/int(h)
        obj_width_x = float(x2-x1)/int(w)
        obj_height_y = float(y2-y1)/int(h)
        obj_class = classes.index(label[6])
        formatted_file.write("%d %f %f %f %f\n"%(obj_class, center_x_f, center_y_f, obj_width_x, obj_height_y)) 
    formatted_file.close()
print("done")
