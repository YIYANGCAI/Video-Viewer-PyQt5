# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtChart import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import random

# Create plot based on matplotlib, which can embed to pyqt5

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        screen = QDesktopWidget().screenGeometry()
        MainWindow.resize(screen.width()-40, screen.height())
        size = self.geometry()
        self.width = self.width()
        width = self.width
        self.height = self.height()
        height = self.height

        self.GroupBox = QGroupBox("Algorithms", self)
        self.check_all = QCheckBox("全选", self)
        self.check_sr = QCheckBox("超分", self)
        self.check_denoise = QCheckBox("降噪", self)
        self.check_color_addition = QCheckBox("上色", self)
        self.check_color_enhance = QCheckBox("色彩增强", self)
        self.check_de_scratch = QCheckBox("去划痕", self)
        self.check_add_frame = QCheckBox("插帧", self)
        self.check_layout = QVBoxLayout()
        self.init_check_layout()
        self.GroupBox.setGeometry(QtCore.QRect(width/120, height/10, width/16, height/4))

        #set six buttons of processing algorithm
        self.btn_sr = QtWidgets.QPushButton(self.centralwidget)
        
        self.btn_sr.setGeometry(QtCore.QRect(width/12, height/60, (width)/12, height/25))
        self.btn_sr.setObjectName("sr")

        self.btn_helper = QtWidgets.QPushButton(self.centralwidget)
        self.btn_helper.setGeometry(QtCore.QRect(width/5, height/60, (width)/12, height/25))
        self.btn_helper.setObjectName("helper")

        # define the area to display original & processed video
        self.FrameDisplayAera_1 = QLabel(self)
        self.FrameDisplayAera_1.setGeometry(QtCore.QRect(width/12, height/15, 0.93*width, height*80/100))
        self.FrameDisplayAera_1.setObjectName("FrameDisplayAera_1")

        self.Logo_airia = QLabel(self)
        self.Logo_airia.setGeometry(QtCore.QRect(width-width/15, height/60, width/12, height/25))
        self.Logo_airia.setObjectName("Logo_airia")
        self.Logo_airia.setPixmap(QPixmap("./icons/airia_new.jpg"))
        self.Logo_airia.setScaledContents(True)

        self.Logo_airia = QLabel(self)
        self.Logo_airia.setGeometry(QtCore.QRect(width/120, height/100, width/15, height/15))
        self.Logo_airia.setObjectName("Logo_airia2")
        self.Logo_airia.setPixmap(QPixmap("./icons/airiaVE3.png"))
        self.Logo_airia.setScaledContents(True)

        # slider to display video's playing process
        self.sld_video = QtWidgets.QSlider(self.centralwidget)
        self.sld_video.setGeometry(QtCore.QRect(width*3/20, height*895/1000, width-width/6, height/60))
        #self.sld_video.setMaximum(100)
        self.sld_video.setOrientation(QtCore.Qt.Horizontal)
        self.sld_video.setObjectName("sld_video")

        # slider to set the seperation line
        self.sld_division = QtWidgets.QSlider(self.centralwidget)
        self.sld_division.setGeometry(QtCore.QRect(width/2, height/50, width-width*2/3, height/60))
        self.sld_division.setMaximum(100)
        self.sld_division.setOrientation(QtCore.Qt.Horizontal)
        self.sld_division.setObjectName("sld_division")

        self.lab_division = QtWidgets.QLabel(self.centralwidget)
        self.lab_division.setGeometry(QtCore.QRect(width*2/5, height/80, width/6, height/35))
        self.lab_division.setObjectName("lab_video")

        self.btn_playorpause = QtWidgets.QPushButton(self.centralwidget)
        self.btn_playorpause.setGeometry(QtCore.QRect(width/12, 89*height/100, width/40, height/35))

        self.btn_stop = QtWidgets.QPushButton(self.centralwidget)
        self.btn_stop.setGeometry(QtCore.QRect(width/9, height*89/100, width/40, height/35))

        self.lab_video = QtWidgets.QLabel(self.centralwidget)
        self.lab_video.setGeometry(QtCore.QRect(width - width/100, height*89/100, width/20, height/35))
        self.lab_video.setObjectName("lab_video")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 568, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        print("width\t",width)
        print("height\t",height)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    
    def retranslateUi(self, MainWindow):
        names = ["文件", "帮助"]
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_sr.setText(_translate("MainWindow",names[0]))
        self.btn_helper.setText(_translate("MainWindow",names[1]))
        #self.btn_hei.setText(_translate("MainWindow",names[2]))
        #self.btn_color.setText(_translate("MainWindow",names[3]))
        #self.btn_fps.setText(_translate("MainWindow",names[4]))
        #self.btn_repair.setText(_translate("MainWindow",names[5]))
        self.lab_video.setText(_translate("MainWindow", "0%"))
        self.lab_division.setText(_translate("MainWindow", "原图/处理后图分割比例:\t30:70"))
        self.sld_division.setValue(30)


    def init_check_layout(self):
        self.check_layout.addWidget(self.check_all)
        self.check_layout.addWidget(self.check_sr)
        self.check_layout.addWidget(self.check_denoise)
        self.check_layout.addWidget(self.check_color_addition)
        self.check_layout.addWidget(self.check_color_enhance)
        self.check_layout.addWidget(self.check_de_scratch)
        self.check_layout.addWidget(self.check_add_frame)
        self.GroupBox.setLayout(self.check_layout)