#-------------------------------------------------------------------------------
# Name:        Object bounding box label tool
# Purpose:     Label object bboxes for ImageNet Detection data
# Author:      Qiushi, modifications made by Andrew Hu
# Created:     03/13/2019
#
#-------------------------------------------------------------------------------
from __future__ import division
from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk
import os
import glob
import random
from shutil import move as move_file

# colors for the bboxes
COLORS = ['red', 'blue', 'teal', 'magenta', 'green', 'olive',  'black', 'grey', 'cyan']
# image sizes for the examples
SIZE = 256, 256

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool 9000")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)

        self.line_size = 2

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = "examples"
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None
        self.currentLabelclass = ''
        self.cla_can_temp = []
        self.classcandidate_filename = 'classes.txt'

        # Current image dimensions
        self.w, self.h = 0, 0

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text = "Image Dir:")
        self.label.grid(row = 0, column = 0, sticky = E)
        # self.entry = Entry(self.frame)
        # self.entry = StringVar()
        self.foldername = StringVar()
        self.entry = ttk.Combobox(self.frame, state='readonly', textvariable=self.foldername)
        self.entry.grid(row = 0, column = 1, sticky = W+E)
        self.entry['values'] = os.listdir('Images')
        if os.path.exists('./Images/examples'):
            self.entry.current(self.entry['values'].index('examples'))
        self.foldername.trace("w", self.loadDir)
        # self.ldBtn = Button(self.frame, text = "Load", command = self.loadDir)
        # self.ldBtn.grid(row = 0, column = 2,sticky = W+E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("a", self.prevImage) # press 'a' to go backforward
        self.parent.bind("<Left>", self.prevImage)
        self.parent.bind("<Right>", self.nextImage)
        self.parent.bind("d", self.nextImage) # press 'd' to go forward
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)


      


        # choose class
        self.classlabel = Label(self.frame, text = "Class:")
        self.classlabel.grid(row=0, column=2, sticky=W+N)
        self.classname = StringVar()
        self.classcandidate = ttk.Combobox(self.frame,state='readonly',textvariable=self.classname, width=26)
        self.classcandidate.grid(row=1,column=2)
        if os.path.exists(self.classcandidate_filename):
        	with open(self.classcandidate_filename) as cf:
        		for line in cf.readlines():
        			self.cla_can_temp.append(line.strip('\n'))
        #print self.cla_can_temp
        self.classcandidate['values'] = self.cla_can_temp
        self.classcandidate.current(0)
        self.currentLabelclass = self.classcandidate.get() #init
        # self.btnclass = Button(self.frame, text = 'ComfirmClass', command = self.setClass)
        # self.btnclass.grid(row=2,column=2,sticky = W+E)

        self.classname.trace("w", self.setClass) 

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 3, column = 2,  sticky = W+N)
        self.listbox = Listbox(self.frame, width = 30, height = 12)
        self.listbox.grid(row = 4, column = 2, sticky = N+S)
        self.btnDel = Button(self.frame, text = 'Delete', command = self.delBBox)
        self.btnDel.grid(row = 5, column = 2, sticky = W+E+N)
        self.btnClear = Button(self.frame, text = 'ClearAll', command = self.clearBBox)
        self.btnClear.grid(row = 6, column = 2, sticky = W+E+N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 7, column = 1, columnspan = 2, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = LEFT, padx=5)
        self.discardImageBtn = Button(self.ctrPanel, text='Discard', command=self.discardImage)
        self.discardImageBtn.pack(side = LEFT)

          # Current image info
        self.currentimage = Label(self.ctrPanel)
        self.currentimage.pack(side= LEFT)


        # example pannel for illustration
        self.egPanel = Frame(self.frame, border = 10)
        self.egPanel.grid(row = 1, column = 0, rowspan = 5, sticky = N)
        # self.tmpLabel2 = Label(self.egPanel, text = "Examples:")
        # self.tmpLabel2.pack(side = TOP, pady = 5)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side = TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)

        if os.path.exists('./Images/examples'):
            self.loadDir()

        # for debugging
##        self.setImage()
##        self.loadDir()

    def discardImage(self, *argv):
        if not os.path.exists("./Images/_trash"):
            os.mkdir("./Images/_trash")
        im_name = self.currentimage['text'].split('\\')[-1]

        move_file(self.currentimage['text'], os.path.join("./Images/_trash", im_name))
        
        cur_img = self.cur
        self.loadDir()
        self.cur = cur_img
        if self.cur > self.total:
            self.cur = self.total
        self.loadImage()


    def loadDir(self, dbg = False, *argv):
        if dbg:
            s = self.entry.get()
            print("self.entry", s)
            self.parent.focus()
            self.category = s
        else:
            s = r'D:\workspace\python\labelGUI'
##        if not os.path.isdir(s):
##            tkMessageBox.showerror("Error!", message = "The specified dir doesn't exist!")
##            return
        # get image list
        self.imageDir = os.path.join(r'./Images', self.category)
        print("Image Directory:", self.imageDir)
        #print self.imageDir 
        #print self.category
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        #print self.imageList
        if len(self.imageList) == 0:
            print('No .jpg images found in the specified dir!')
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

         # set up output dir
        self.outDir = os.path.join(r'./Labels', self.category)
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        # load example bboxes
        #self.egDir = os.path.join(r'./Examples', '%03d' %(self.category))
        #self.egDir = os.path.join(r'./Examples/demo')
        #print(os.path.exists(self.egDir))
        #if not os.path.exists(self.egDir):
        #    return
        #filelist = glob.glob(os.path.join(self.egDir, '*.jpg'))
        #self.tmp = []
        #self.egList = []
        #random.shuffle(filelist)
        #for (i, f) in enumerate(filelist):
        #    if i == 3:
        #        break
        #    im = Image.open(f)
        #    r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
        #    new_size = int(r * im.size[0]), int(r * im.size[1])
        #    self.tmp.append(im.resize(new_size, Image.ANTIALIAS))
        #    self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
        #    self.egLabels[i].config(image = self.egList[-1], width = SIZE[0], height = SIZE[1])

        self.loadImage()
        print('%d images loaded from %s' %(self.total, s))

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        self.currentimage['text'] = imagepath
        self.img = Image.open(imagepath)
        self.w, self.h = self.img.size
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))

        # load labels
        self.clearBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    tmp =line.split()
                    self.w, self.h = [int(tmp[4]), int(tmp[5])]

                    self.bboxList.append(tuple(tmp))
                    tmpId = self.mainPanel.create_rectangle(int(tmp[0]), int(tmp[1]), \
                                                            int(tmp[2]), int(tmp[3]), \
                                                            width = self.line_size, \
                                                            outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    text_len = len(tmp[6])
                    labelbox_id = self.mainPanel.create_rectangle(int(tmp[0]), int(tmp[1]), \
                                                            int(tmp[0])+text_len*7, int(tmp[1])+12, \
                                                                fill = COLORS[(len(self.bboxList)-1) % len(COLORS)], \
                                                                    outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    label_id = self.mainPanel.create_text((int(tmp[0])+3, int(tmp[1])-3), anchor=NW, text=tmp[6], fill="#FFFFFF", font="monospace 10")
                    self.bboxIdList.append((tmpId, labelbox_id, label_id))
                    self.listbox.insert(END, '%s : (%d, %d) -> (%d, %d)' %(tmp[6],int(tmp[0]), int(tmp[1]), \
                    												  int(tmp[2]), int(tmp[3])))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

    def saveImage(self):
        with open(self.labelfilename, 'w') as f:
            for bbox in self.bboxList:
                f.write(' '.join(map(str, bbox)) + '\n')
        print('Image No. %d saved to %s' %(self.cur, self.labelfilename))


    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.bboxList.append((x1, y1, x2, y2, self.w, self.h, self.currentLabelclass))
            text_len = len(self.currentLabelclass)
            labelbox_id = self.mainPanel.create_rectangle(x1, y1, \
                                                            x1+text_len*7, y1+12, \
                                                            fill = COLORS[(len(self.bboxList)-1) % len(COLORS)], \
                                                            outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
            label_id = self.mainPanel.create_text((x1+3, y1-3), anchor=NW, text=self.currentLabelclass, fill="#FFFFFF", font="Helvetica 10")
            self.bboxIdList.append((self.bboxId, labelbox_id, label_id))
            self.bboxId = None
            self.listbox.insert(END, '%s : (%d, %d) -> (%d, %d)' %(self.currentLabelclass,x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = self.line_size)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = self.line_size)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                            event.x, event.y, \
                                                            width = self.line_size, \
                                                            outline = COLORS[len(self.bboxList) % len(COLORS)])

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx][0])
        self.mainPanel.delete(self.bboxIdList[idx][1])
        self.mainPanel.delete(self.bboxIdList[idx][2])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx][0])
            self.mainPanel.delete(self.bboxIdList[idx][1])
            self.mainPanel.delete(self.bboxIdList[idx][2])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []

    def prevImage(self, event = None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event = None):
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()

    def setClass(self, *argv):
    	self.currentLabelclass = self.classcandidate.get()
    	print('set label class to :',self.currentLabelclass)

    # def setFolder(self, *argv):
    #     self.

##    def setImage(self, imagepath = r'test2.png'):
##        self.img = Image.open(imagepath)
##        self.tkimg = ImageTk.PhotoImage(self.img)
##        self.mainPanel.config(width = self.tkimg.width())
##        self.mainPanel.config(height = self.tkimg.height())
##        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width =  True, height = True)
    root.mainloop()
