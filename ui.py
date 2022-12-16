
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
import cv2, imutils
import time
import numpy as np
import pyshine as ps
from threading import Thread
import sys
import os 
from datetime import datetime
from model import load_model

model = load_model()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(498, 522)
        self.mw  = MainWindow
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("images/face.jpg"))
        self.label.setObjectName("label")

        # adding another label for second video
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap("images/vehicle.jpg"))
        self.label_4.setObjectName("label")

        self.horizontalLayout.addWidget(self.label)
        self.horizontalLayout.addWidget(self.label_4)


        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.verticalSlider = QtWidgets.QSlider(self.centralwidget)
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setObjectName("verticalSlider")
        self.gridLayout.addWidget(self.verticalSlider, 0, 0, 1, 1)
        self.verticalSlider_2 = QtWidgets.QSlider(self.centralwidget)
        self.verticalSlider_2.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_2.setObjectName("verticalSlider_2")
        self.gridLayout.addWidget(self.verticalSlider_2, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 1, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_2.addWidget(self.pushButton_2)

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_2.addWidget(self.pushButton_3)

        self.gridLayout_2.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(313, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 1, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.verticalSlider.valueChanged['int'].connect(self.brightness_value)
        self.verticalSlider_2.valueChanged['int'].connect(self.blur_value)

        self.th = {}
        self.pushButton_2.clicked.connect(self.run_threads)
        self.pushButton_3.clicked.connect(self.run_threads)
        self.pushButton.clicked.connect(self.savePhoto)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        # Added code here
        self.filename = 'Snapshot '+str(time.strftime("%Y-%b-%d at %H.%M.%S %p"))+'.png' # Will hold the image address location
        self.tmp = None # Will hold the temporary image for display
        self.tmp2 = None # Will hold the temporary image for display2
        self.brightness_value_now = 0 # Updated brightness value
        self.blur_value_now = 0 # Updated blur value
        self.fps=0
        
        self.started = False
        self.started2 = False
        
        
        # Check camera
        self.available_cameras = QCameraInfo.availableCameras()

        if not self.available_cameras:
            # exit the code
            sys.exit()
            

    def play_videos(self,notePath):
        print(notePath)
        if notePath == 'pushButton_2':
            self.loadImage()
        if notePath == 'pushButton_3':
            self.loadImage2()
	
    def run_threads(self):
        self.th[self.mw.sender().objectName()] = Thread(target = self.play_videos, args = (self.mw.sender().objectName(),)) 
        self.th[self.mw.sender().objectName()].start()
        
    def loadImage(self):
        print([camera.description() for camera in self.available_cameras])
        """ This function will load the camera device, obtain the image
            and set it to label using the setPhoto function
        """
        try:
            faceCascade = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')
        except Exception as e:
            print('Warning...',e)
        if self.started:
            self.started=False
            self.pushButton_2.setText('Open Face')	
        else:
            self.started=True
            self.pushButton_2.setText('Stop')
        
        cam = False # True for webcam
        if cam:
            vid = cv2.VideoCapture(0)
        else:
            vid = cv2.VideoCapture('videos/Bikers and Carriages Driving on Street.mp4')
        
        cnt=0
        frames_to_count=20
        st = 0
        fps=0
        
        while(vid.isOpened()):
            # QtWidgets.QApplication.processEvents()	
            _, image = vid.read()
            image  = imutils.resize(image ,height = 480 )
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
            try:
                faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.15,  
                minNeighbors=7, 
                minSize=(80, 80), 
                flags=cv2.CASCADE_SCALE_IMAGE)
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x, y), (x + w, y + h), (10, 228,220), 5) 
            except Exception as e:
                pass
            
            if cnt == frames_to_count:
                try: # To avoid divide by 0 we put it in try except
                    print(frames_to_count/(time.time()-st),'FPS') 
                    fps = round(frames_to_count/(time.time()-st)) 
                    st = time.time()
                    cnt=0
                except:
                    pass
            
            cnt+=1
            
            self.update(image,self.label,fps)
            key = cv2.waitKey(1) & 0xFF
            if self.started==False:
                break
        
        vid.release()
        cv2.destroyAllWindows()
        
    def loadImage2(self):
        """ This function will load the camera device, obtain the image
            and set it to label using the setPhoto function
        """
        try:
            faceCascade = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')
        except Exception as e:
            print('Warning...',e)
        if self.started2:
            self.started2=False
            self.pushButton_3.setText('Open Plate')	
        else:
            self.started2=True
            self.pushButton_3.setText('Stop')
        
        cam = True # True for webcam
        if cam:
            vid = cv2.VideoCapture(2)
        else:
            vid = cv2.VideoCapture('videos/Bikers and Carriages Driving on Street.mp4')
        
        cnt=0
        frames_to_count=5
        st = 0
        fps=0
        
        while(vid.isOpened()):
            # QtWidgets.QApplication.processEvents()	
            _, image = vid.read()
            
            # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
            # try:
            #     faces = faceCascade.detectMultiScale(
            #     gray,
            #     scaleFactor=1.15,  
            #     minNeighbors=7, 
            #     minSize=(80, 80), 
            #     flags=cv2.CASCADE_SCALE_IMAGE)
                
            #     for (x, y, w, h) in faces:
            #         cv2.rectangle(image, (x, y), (x + w, y + h), (10, 228,220), 5) 
            # except Exception as e:
            #     pass
            
            if cnt == frames_to_count:

                    image  = imutils.resize(image ,height = 480 )
                    cv2.imwrite("temp.jpg", image)
                    print("take")
                    predictions = model.predict("temp.jpg", confidence=50, overlap=30).json()
                    print(predictions)
                    for pred in predictions['predictions']:
                        x, y, w, h = pred['x'], pred['y'], pred['width'], pred['height']
                        class_name = pred["class"]
                        cv2.rectangle(image, 
                                (int(x-w/2), int(y+h/2)),
                                (int(x+w/2), int(y-h/2)),
                                (255, 0, 0), 2)
                                        # Get size of text
                        text_size = cv2.getTextSize(
                            class_name, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1
                        )[0]
                        # Draw background rectangle for text
                        cv2.rectangle(
                            image,
                            (int(x - w / 2), int(y - h / 2 + 1)),
                            (
                                int(x - w / 2 + text_size[0] + 1),
                                int(y - h / 2 + int(1.5 * text_size[1])),
                            ),
                            (255, 0, 0),
                            -1,
                        )
                        # Write text onto image
                        cv2.putText(
                            image,
                            class_name,
                            (int(x - w / 2), int(y - h / 2 + text_size[1])),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,
                            (255, 255, 255),
                            thickness=1,
                        )                        

                    print(frames_to_count/(time.time()-st),'FPS') 
                    fps = round(frames_to_count/(time.time()-st)) 
                    st = time.time()
                    cnt=0

            
            cnt+=1
            
            self.update(image,self.label_4,fps)
            key = cv2.waitKey(1) & 0xFF
            if self.started2==False:
                break

    def setPhoto(self,image, label):
        """ This function will take image input and resize it 
            only for display purpose and convert it to QImage
            to set at the label.
        """
        if label is self.label:
            self.tmp = image
        if label is self.label_4:
            self.tmp2 = image
        image = imutils.resize(image,width=640)
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
        label.setPixmap(QtGui.QPixmap.fromImage(image))

    def brightness_value(self,value):
        """ This function will take value from the slider
            for the brightness from 0 to 99
        """
        self.brightness_value_now = value
        print('Brightness: ',value)
        #self.update()
        
        
    def blur_value(self,value):
        """ This function will take value from the slider 
            for the blur from 0 to 99 """
        self.blur_value_now = value
        print('Blur: ',value)
        #self.update()


    def changeBrightness(self,img,value):
        """ This function will take an image (img) and the brightness
            value. It will perform the brightness change using OpenCv
            and after split, will merge the img and return it.
        """
        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(hsv)
        lim = 255 - value
        v[v>lim] = 255
        v[v<=lim] += value
        final_hsv = cv2.merge((h,s,v))
        img = cv2.cvtColor(final_hsv,cv2.COLOR_HSV2BGR)
        return img
        
    def changeBlur(self,img,value):
        """ This function will take the img image and blur values as inputs.
            After perform blur operation using opencv function, it returns 
            the image img.
        """
        kernel_size = (value+1,value+1) # +1 is to avoid 0
        img = cv2.blur(img,kernel_size)
        return img

    def update(self,image,label,fps):
        """ This function will update the photo according to the 
            current values of blur and brightness and set it to photo label.
        """
        img = self.changeBrightness(image,self.brightness_value_now)
        img = self.changeBlur(img,self.blur_value_now)

        # Here we add display text to the image
        text  =  'FPS: '+str(fps)
        img = ps.putBText(img,text,text_offset_x=20,text_offset_y=30,vspace=20,hspace=10, font_scale=1.0,background_RGB=(10,20,222),text_RGB=(255,255,255))
        text = str(time.strftime("%H:%M %p"))
        img = ps.putBText(img,text,text_offset_x=image.shape[1]-180,text_offset_y=30,vspace=20,hspace=10, font_scale=1.0,background_RGB=(228,20,222),text_RGB=(255,255,255))
        text  =  f"Brightness: {self.brightness_value_now}"
        img = ps.putBText(img,text,text_offset_x=80,text_offset_y=425,vspace=20,hspace=10, font_scale=1.0,background_RGB=(20,210,4),text_RGB=(255,255,255))
        text  =  f'Blur: {self.blur_value_now}: '
        img = ps.putBText(img,text,text_offset_x=image.shape[1]-200,text_offset_y=425,vspace=20,hspace=10, font_scale=1.0,background_RGB=(210,20,4),text_RGB=(255,255,255))


        self.setPhoto(img,label)

    def savePhoto(self):
        date = str(datetime.now().date()).replace("-","")
        img_path = "images/" + date + "/"
        if os.path.isdir(img_path) == False:
            os.mkdir(img_path)
        
        """ This function will save the image"""
        self.filename = 'Snapshot v1'+str(time.strftime("%Y-%b-%d at %H.%M.%S %p"))+'.png'
        self.filename2 = 'Snapshot v2'+str(time.strftime("%Y-%b-%d at %H.%M.%S %p"))+'.png'
        if self.tmp is not None:
            cv2.imwrite(img_path + self.filename,self.tmp)
            print('Image saved as:', img_path + self.filename)
        if self.tmp2 is not None:
            cv2.imwrite(img_path + self.filename2,self.tmp2)
            print('Image saved as:',img_path + self.filename2)
    

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Parking Track - SV From SPKT HCM"))
        self.pushButton_2.setText(_translate("MainWindow", "Open Face"))
        self.pushButton_3.setText(_translate("MainWindow", "Open Plate"))
        self.label_2.setText(_translate("MainWindow", "Brightness"))
        self.label_3.setText(_translate("MainWindow", "Blur"))
        self.pushButton.setText(_translate("MainWindow", "Take picture"))



# if __name__ == "__main__":
# 	import sys
# 	app = QtWidgets.QApplication(sys.argv)
# 	MainWindow = QtWidgets.QMainWindow()
# 	ui = Ui_MainWindow()
# 	ui.setupUi(MainWindow)
# 	MainWindow.show()
# 	sys.exit(app.exec_())
