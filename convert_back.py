import os
from PIL import Image

images = os.listdir("Images/001")
labels = [i[:-4]+".txt" for i in images]

for l in labels:
    lines = open("Labels/001/convert/"+l).read().splitlines()
    f = open("Labels/001/"+l, "w")
    w, h = Image.open("Images/001/"+l[:-4]+".jpg").size
    for line in lines:
        line = line.split()
        cls = None
        if line[0] == '0':
            cls = "traffic_drum"
        elif line[0] == '1':
            cls = "person"
        elif line[0] == '2':
            cls = "stop_sign"
        elif line[0] == '3':
            cls = "one_way_sign"
        else:
            print("WUT")
            break
        nums = [float(x) for x in line[1:]]
        box_w, box_h = nums[2]*w, nums[3]*h
        ctr_x, ctr_y = nums[0]*w, nums[1]*h
        x1, y1 = int(ctr_x-box_w/2), int(ctr_y-box_h/2)
        x2, y2 = int(ctr_x+box_w/2), int(ctr_y+box_h/2)
        f.write("%d %d %d %d %d %d %s\n" % (x1,y1,x2,y2,w,h,cls))
        
    f.close()
