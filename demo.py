# -*- coding: utf-8 -*-

import os, sys, time
import shutil
import copy
import cv2 as cv
import numpy as np
import random
# embedding pyqt5 with matplotlib requires special announcement
from PIL import Image

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtChart import *
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QDesktopWidget
from GUI import Ui_MainWindow

# add self designed process algorithm and parameter measurement
from Algorithm import ProcessAlgorithm
from Evaluation import EvaluationParameter

class VideoWindow(Ui_MainWindow,QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.screen=QApplication.primaryScreen()
        self.setupUi(self)
        self.InitFrame("./icons/default1.jpg")
        self.show()

        self.cwd = os.getcwd()
        self.tlx=0
        self.tly=0
        self.brx=0
        self.bry=0
        # set some status variable of the video
        self.flag = 1 # "1" means the status of pause
        self.SetBtnIcon()
        self.loaded = 0 #0 means that the video is not loaded, self.lrcap is empty
        self.first_frame_label = 0 #0 means that the video is loaded and not at the beginning frame

        # define the parameters of the video
        self.delay_time = 0
        self.total_frames = 0
        self.load_success = False #initial status of the video
        self.current_frame_id = 0

        # define events of opening files
        self.btn_sr.clicked.connect(self.LoadVideo)
        # setup a timer to play the video
        # the time is related to the video's fps
        self.FrameTrigger = QTimer(self)
        self.FrameTrigger.timeout.connect(self.PlayVideo)

        # define the playorpause button
        self.btn_playorpause.clicked.connect(self.StartOrPauseTrigger)
        self.btn_playorpause.setEnabled(False)

        self.btn_stop.clicked.connect(self.ShuttoBeginning)
        self.btn_stop.setIcon(QIcon("./icons/end.jpg"))
        self.btn_stop.setEnabled(False)

        self.btn_helper.clicked.connect(self.HelpDialogShow)

        self.evaluation_toolbox = EvaluationParameter()
        self.algorithm_pool = ProcessAlgorithm()

        self.check_all.stateChanged.connect(self.Changecb_1)
        self.check_color_addition.stateChanged.connect(self.Changecb_2)
        self.check_color_enhance.stateChanged.connect(self.Changecb_2)
        self.check_de_scratch.stateChanged.connect(self.Changecb_2)
        self.check_denoise.stateChanged.connect(self.Changecb_2)
        self.check_sr.stateChanged.connect(self.Changecb_2)
        self.check_add_frame.stateChanged.connect(self.Changecb_2)

        self.sld_division.valueChanged.connect(self.change_division_value)
        self.sld_video.valueChanged.connect(self.pause_change_frame)
        self.ShuttoBeginning_state = 0
        self.Jump_to_beginning_status = 0
        self.VideoLoaded = 0

    def HelpDialogShow(self):
    	dialog = QDialog()
    	btn = QPushButton("OK", dialog)
    	btn.move(50, 50)
    	dialog.setWindowTitle("Helper")
    	dialog.setWindowModality(Qt.ApplicationModal)
    	dialog.exec_()

    def NoFileWarming(self):
        Nofile_dialog = QMessageBox.warning(
            self, 
            "Warning",
            "No video file is selected, Please retry.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if (Nofile_dialog == QMessageBox.Yes):
            self.LoadVideo()
        else:
            return

    def InitFrame(self, DefaultPicture):
        self.FrameDisplayAera_1.setPixmap(QPixmap(DefaultPicture))
        self.FrameDisplayAera_1.setScaledContents(True)
        #self.FrameDisplayAera_2.setPixmap(QPixmap(DefaultPicture))
        #self.FrameDisplayAera_2.setScaledContents(True)

    def ChangeFrame(self, preprocessed_frame):
        show1 = cv.cvtColor(preprocessed_frame, cv.COLOR_BGR2RGB)
        showImage1 = QImage(
            show1.data, 
            show1.shape[1], 
            show1.shape[0], 
            QImage.Format_RGB888
        )     
        self.FrameDisplayAera_1.setPixmap(QPixmap.fromImage(showImage1))

    def show_lr_hr(self, framelr, framehr):
        ratio = self.division/100.
        h,w,c = framehr.shape
        print('...................HR: ', framehr.shape)
        print("self.height:{};self.width:{}".format(self.height, self.width))
        print("height:{};width:{}".format(h, w))
        newframehr = cv.resize(framehr, (w,h))
        newframelr = cv.resize(framelr, (w,h))
        newframe = copy.deepcopy(newframehr)
        newframe[:, 0:int(w*ratio), :] = newframelr[:, 0:int(w*ratio), :]
        newframe[:, int(w*ratio):w, :] = newframehr[:, int(w*ratio):w, :]
        newframe[:, int(w*ratio):(int(w*ratio)+2), 0] = 255
        newframe[:, int(w*ratio):(int(w*ratio)+2), 1] = 0
        newframe[:, int(w*ratio):(int(w*ratio)+2), 2] = 0 
        # the follwoing code is to add a margin of the original frames
        r1 = self.width / self.height
        r2 = w / h
        print("r1:",r1)
        print("r2:",r2)
        if r1>r2:
            margin = int((h*self.width/self.height - w)/2)-1
            print("margin_value:", margin)
            #newframe = cv.copyMakeBorder(newframe,margin,margin,0,0,cv.BORDER_CONSTANT,value=[0,0,0])
            newframe = cv.copyMakeBorder(newframe,0,0,margin,margin,cv.BORDER_CONSTANT,value=[0,0,0])
        else:
            margin = int((w*self.height/self.width - h)/2)-1
            print("margin_value:", margin)
            #newframe = cv.copyMakeBorder(newframe,0,0,margin,margin,cv.BORDER_CONSTANT,value=[0,0,0])
            newframe = cv.copyMakeBorder(newframe,margin,margin,0,0,cv.BORDER_CONSTANT,value=[0,0,0])
        return newframe

    def update_frame(self):
        position_id = self.sld_video.value()
        self.current_frame_id = position_id
        print("+++++++++++position:", position_id)
        self.lab_video.setText(str(round(position_id*100/self.total_frames))+'%')
        lrimg_path = self.os_path_join(self.lr_dir, str(position_id)+'.bmp')
        hrimg_path = self.os_path_join(self.hr_dir, str(position_id)+'.bmp')
        framelr = cv.imread(lrimg_path)
        framehr = cv.imread(hrimg_path)
        self.change_division_value()
        newframe = self.show_lr_hr(framelr, framehr)
        self.ChangeFrame(newframe)

    def LoadProgressBar_1(self):
        self.pb_1 = QProgressDialog(self)
        self.pb_1.setWindowTitle("Loading the LR video")
        self.pb_1.setLabelText("Loading the LR video...")
        self.pb_1.setCancelButtonText("Cancel")
        self.pb_1.setRange(0,self.total_frames)
        self.pb_1.setValue(0)
        self.pb_1.open()

    def LoadProgressBar_2(self):
        self.pb_2 = QProgressDialog(self)
        self.pb_2.setWindowTitle("Loading the HR video")
        self.pb_2.setLabelText("Loading the HR video")
        self.pb_2.setCancelButtonText("Cancel")
        self.pb_2.setRange(0,self.total_frames)
        self.pb_2.setValue(0)
        self.pb_2.open()

    def LoadVideo(self):
        self.OriginalVideoPath, VideoType = QFileDialog.getOpenFileName(
            self,
            "Video File Selection",
            self.cwd,
            "Video files (*.mp4)"
        )
        if self.OriginalVideoPath != "":
            self.VideoLoaded = 1
        else:
            self.NoFileWarming()
            return
        # load the original video

        self.lrcap = cv.VideoCapture(self.OriginalVideoPath)
        self.total_frames = self.lrcap.get(7)
        (self.file_theme, self.extension) = os.path.splitext(self.OriginalVideoPath)
        print("Load the original video:{}".format(self.OriginalVideoPath))
        
        hrfile= self.file_theme+'-HR.mp4'
        print('..........................', hrfile)
        self.hrcap = cv.VideoCapture(hrfile)
        self.lr_dir = self.file_theme

        if os.path.exists(self.lr_dir) and len(os.listdir(self.lr_dir)) != self.total_frames:
            print("LR files error...")
            shutil.rmtree(self.lr_dir)
        if not os.path.exists(self.lr_dir):
            self.LoadProgressBar_1()
            os.makedirs(self.lr_dir)
            load_success_1, framelr = self.lrcap.read()
            self.ChangeFrame(framelr)
            k_lr = 0
            print('.......................load LR video ...') 
            while(load_success_1):
                print('....lr writing : {}'.format(k_lr))
                imglr_file = self.os_path_join(self.lr_dir, str(k_lr)+'.bmp')
                cv.imwrite(imglr_file, framelr)
                load_success_1, framelr = self.lrcap.read()
                k_lr += 1
                self.pb_1.setValue(k_lr)
                QApplication.processEvents()
            print('.......................load LR video done.')
        else:
            print('.......................load LR video done.')


        self.hr_dir = self.file_theme + '-HR'
        if os.path.exists(self.hr_dir) and len(os.listdir(self.hr_dir)) != self.total_frames:
            print("HR files error...")
            shutil.rmtree(self.hr_dir)
        if not os.path.exists(self.hr_dir):
            self.LoadProgressBar_2()
            os.makedirs(self.hr_dir) 
            load_success_2, framehr = self.hrcap.read()
            k_hr = 0
            print('.......................load HR video ...')
            print("load_success_2:",load_success_2)
            while(load_success_2):
                print('....hr writing : {}'.format(k_hr))
                imghr_file = self.os_path_join(self.hr_dir, str(k_hr)+'.bmp')
                cv.imwrite(imghr_file, framehr)
                load_success_2, framehr = self.hrcap.read()
                k_hr += 1
                self.pb_2.setValue(k_hr)
                QApplication.processEvents()
            print('.......................load HR video done.')
        else:
            print('.......................load HR video done.')
        self.loaded = 1 #alter the state variable
        self.btn_playorpause.setIcon(QIcon("./icons/play.jpg"))
        self.btn_playorpause.setEnabled(True)
        self.btn_stop.setEnabled(True)

        #load_success, self.frame = self.lrcap.read()
        #load_success_gdt, self.frame_gdt = self.CapGroundtruth.read()
        #self.ChangeFrame(self.frame)
        self.delay_time = (1.0 / self.lrcap.get(5)) * 500
        self.sld_video.setMaximum(self.total_frames)
        self.current_frame_id = 0
        # when we change the id of the frame, we remember to change the slider
        self.ChangeSlider()
        self.sld_video.setValue(0)
        self.update_frame()
        self.first_frame_label = 1
        #self.ClearPointSeries()

    def pause_change_frame(self):
        if self.ShuttoBeginning_state == 1:
            self.ShuttoBeginning_state = 0
            return
        elif self.flag == 0:
            return
        else:
            self.update_frame() 

    def os_path_join(self, a, b):
        return a +'/' + b

    def ShuttoBeginning(self):
        self.ShuttoBeginning_state = 1
        self.current_frame_id = self.total_frames
        self.JumpToBeginning()
        position_id = 0
        self.lab_video.setText(str(round(position_id*100/self.total_frames))+'%')

        lrimg_path = self.os_path_join(self.lr_dir, str(position_id)+'.bmp')
        hrimg_path = self.os_path_join(self.hr_dir, str(position_id)+'.bmp')
        framelr = cv.imread(lrimg_path)
        framehr = cv.imread(hrimg_path)
        self.change_division_value()
        newframe = self.show_lr_hr(framelr, framehr)
        self.ChangeFrame(newframe)
        self.sld_video.setValue(0)

    def JumpToBeginning(self):
        if self.current_frame_id == (self.total_frames):
            self.Jump_to_beginning_status = 1
            print("reload the video")
            self.lrcap = cv.VideoCapture(self.OriginalVideoPath)
            self.lrcap = self.lrcap
            #After the video is load, initialize the area into the first frame
            self.load_success, self.frame = self.lrcap.read()
            #self.load_success_gdt, self.frame_gdt = self.CapGroundtruthTemp.read()
            #self.ChangeFrame(self.frame)
            self.flag = 1
            self.SetBtnIcon()
            self.FrameTrigger.stop()
            self.current_frame_id = 0
            #self.ChangeSlider()
            #
            self.lab_video.setText('0%')
            self.first_frame_label = 1
            #Reset the linechart
            #self.InitPointSeries()
        else:
            pass
    
    def SetBtnIcon(self):
        if self.flag == 1:
            self.btn_playorpause.setIcon(QIcon("./icons/play.jpg"))
        else:
            self.btn_playorpause.setIcon(QIcon("./icons/pause.jpg"))

    def PlayVideo(self):
        position_id = self.sld_video.value()
        if self.first_frame_label == 1:
            print("the first load+++++")
            self.first_frame_label = 0
            self.Jump_to_beginning_status = 0
            #self.sld_video.setValue(0)
            #self.ChangeSlider()
            position_id = 0
        
        self.current_frame_id = position_id
        print("position in playing:", position_id)
        lrimg_path = self.os_path_join(self.lr_dir, str(position_id)+'.bmp')
        hrimg_path = self.os_path_join(self.hr_dir, str(position_id)+'.bmp')
        framelr = cv.imread(lrimg_path)
        framehr = cv.imread(hrimg_path)
        self.change_division_value()
        newframe = self.show_lr_hr(framelr, framehr)
        # play the video via read the next frame
        self.ChangeFrame(newframe)
        # change the slider
        
        self.current_frame_id = self.current_frame_id + 1
        self.ChangeSlider()
        self.sld_video.setValue(self.current_frame_id)
        QApplication.processEvents()
        #only when load_success is False, JumpToBeginning is valid                    
        self.JumpToBeginning()

    # def the timeout function
    # when the time if out, read a frame again
    # then as the timer works, the frames changed periodically, acting as a video
    def StartOrPauseTrigger(self):
        if self.flag == 1:
            self.flag = 0
            self.FrameTrigger.start(self.delay_time)
            #self.update_pause()
        else:
            self.flag = 1
            self.FrameTrigger.stop()
        self.SetBtnIcon()
    
    def ChangeSlider(self):
        self.sld_video.setValue(round((self.current_frame_id/self.total_frames)*100))
        #self.PlayVideo()
        self.lab_video.setText(str(round((self.current_frame_id/self.total_frames)*100))+'%')

    def change_division_value(self):
        self.division = self.sld_division.value()
        self.lab_division.setText("原图/处理后图分割比例:\t" + str(self.division) + ":" + str(100-self.division))
        if self.flag == 1:
            print("division:",self.division)
            position_id = self.sld_video.value()
            self.current_frame_id = position_id
            print("+++++++++++position:", position_id)
            if self.Jump_to_beginning_status == 1:
                position_id = position_id - 1
            self.lab_video.setText(str(round(position_id*100/self.total_frames))+'%')
            lrimg_path = self.os_path_join(self.lr_dir, str(position_id)+'.bmp')
            hrimg_path = self.os_path_join(self.hr_dir, str(position_id)+'.bmp')
            framelr = cv.imread(lrimg_path)
            framehr = cv.imread(hrimg_path)
            newframe = self.show_lr_hr(framelr, framehr)
            """
            ratio = self.division/100.
            w,h,c = framehr.shape
            print('...................HR: ', framehr.shape)
            #w = int(w/2)
            #h = int(h/2)

            newframehr = cv.resize(framehr, (w,h))
            newframelr = cv.resize(framelr, (w,h))

            newframe = copy.deepcopy(newframehr) 
            newframe[:, 0:int(w*ratio), :] = newframelr[:, 0:int(w*ratio), :]
            newframe[:, int(w*ratio):(int(w*ratio)+2), 0] = 255
            newframe[:, int(w*ratio):(int(w*ratio)+2), 1] = 0
            newframe[:, int(w*ratio):(int(w*ratio)+2), 1] = 0
            """

        # play the video via read the next frame
            self.ChangeFrame(newframe)

    def Changecb_1(self):
        if self.check_all.checkState() == Qt.Checked:
            self.check_add_frame.setChecked(True)
            self.check_color_addition.setChecked(True)
            self.check_color_enhance.setChecked(True)
            self.check_de_scratch.setChecked(True)
            self.check_denoise.setChecked(True)
            self.check_sr.setChecked(True)
        elif self.check_all.checkState() == Qt.Unchecked:
            self.check_add_frame.setChecked(False)
            self.check_color_addition.setChecked(False)
            self.check_color_enhance.setChecked(False)
            self.check_de_scratch.setChecked(False)
            self.check_denoise.setChecked(False)
            self.check_sr.setChecked(False)
    
    def Changecb_2(self):
        if self.check_add_frame.isChecked() and self.check_color_addition.isChecked() and self.check_color_enhance.isChecked() and self.check_de_scratch.isChecked() and self.check_denoise.isChecked() and self.check_sr.isChecked():
            self.check_all.setCheckState(Qt.Checked)
        elif self.check_add_frame.isChecked() or self.check_color_addition.isChecked() or self.check_color_enhance.isChecked() or self.check_de_scratch.isChecked() or self.check_denoise.isChecked() or self.check_sr.isChecked():
            self.check_all.setTristate()
            self.check_all.setCheckState(Qt.PartiallyChecked)
        else:
            self.check_all.setTristate(False)
            self.check_all.setCheckState(Qt.Unchecked)


def main():
    app = QApplication(sys.argv)
    VideoWindowDemo = VideoWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()