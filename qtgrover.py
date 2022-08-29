# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qtgrover.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal,Qt
from qiskit.visualization import plot_bloch_multivector
from qiskit.visualization import plot_bloch_vector
from qtgroverclass import Grover
import random
# for bloch display use pysimplegui
import matplotlib.pyplot as plt
from PyQt5.QtGui import QPixmap
import os
def binarystring(x, n=0):
    return format(x, 'b').zfill(n)
# Step 1: Create a worker class
class Worker(QObject):
    
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    def __init__(self, objgrover,searchedlist,indexs,datos,bPurity):
        super().__init__()
        self.objgrover = objgrover
        self.searchedlist = searchedlist
        self.indexs = indexs
        self.datos = datos
        self.bPurity = bPurity    
        
    def run(self):        
        """Long-running task."""
        self.objgrover.Search(self.searchedlist,self.indexs,self.datos,self.bPurity)
        #self.progress.emit(i + 1)
        self.finished.emit()

class BlochDialog(QtWidgets.QMainWindow):

    def __init__(self,nImages,simdesc):
        super().__init__()
        self.simdesc = simdesc
        self.nImages = nImages
        self.initUI()
        
    def initUI(self):
        self.scroll = QtWidgets.QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        widget = QtWidgets.QWidget()                 # Widget that contains the collection of Vertical Box
        layout = QtWidgets.QGridLayout()
        size = 200
        column=0
        for k in range(self.nImages-1,-1,-1):
            sfile=os.getcwd() + '/figbloch' + str(k) + '.png'
            object = QtWidgets.QLabel("fila 1")            
            px = QPixmap(sfile).scaled(size,size)            
            object.setPixmap(px)            
            layout.addWidget(object,0,column)
            object = QtWidgets.QLabel(self.simdesc[k])
            object.setFont(QtGui.QFont('Arial', 15))
            layout.addWidget(object,1,column)
            column+=1
        

        #layout.setRowStretch(0, 25)
        layout.setRowStretch(1, 60)
        
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(widget)
        
        self.setCentralWidget(self.scroll)

        self.setGeometry(100, 100, 600, 300)
        self.setWindowTitle('Bloch spheres before measure')
        self.show()

        return

        
                
class Ui_MainWindow(object):
    
    def ShowBlochWindow(self, wposx=0,wposy=0):
        stitle=''
        nq = int(self.numqbits/2)
        
        sfile=os.getcwd() + '/figbloch.png'    
        size = (200, 200)
        stitle='Bloch for index register before measure'
        sdescImg=[]
        for k in range(nq):
            figbloch = plot_bloch_multivector(self.groverobj.GetQubitStateVector(k))
            p = self.groverobj.statevector.probabilities( [k] )
            sdescImg.append ( "Qubit " + str(k) + "\nprob 0 = " + str("%.2f %%"%(p[0]*100)) + "\nprob 1 = " + str("%.2f %%"%(p[1]* 100))) 
            sfile=os.getcwd() + '/figbloch' + str(k) + '.png'
            plt.savefig(sfile,bbox_inches='tight',pad_inches = 0)            
            plt.close('all')
        bdg= BlochDialog(nq,sdescImg)
              
        

    def ThreadGroverHasEnd(self):
        self.listOUT.clear()
        self.listOUT.addItems(self.groverobj.GetResultList())
        self.groverobj.stateSearch = self.groverobj.NOSEARCHING
        self.btGROVER.setText("Grover")
        self.txOUT.append(self.groverobj.txout)
        self.ShowBlochWindow(100,300)
    def RunSearchThread(self,searchedlist,indexs,datos):
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker(self.groverobj,searchedlist,indexs,datos,self.bPurity)
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        #self.worker.finished.connect(self.worker.deleteLater)
        #self.thread.finished.connect(self.thread.deleteLater)
        #self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()
        self.thread.finished.connect(lambda: self.ThreadGroverHasEnd())
                
        
    def createUserBD(self,nvalstofind):    
        nregsdb = 7
        indexs=[0,1,3,6,2,7,4]
        values= [0,3,7,6,5,2,1]
        searchedlist=[values[1],values[2]]
        self.AddTextOut(" USER BD 7 REGISTERS IN DATABASE ")    
        self.AddTextOut("address = "+str( indexs))
        self.AddTextOut("values  = "+str( values))
        self.AddTextOut("search address for values = "+str( searchedlist))
        return searchedlist,indexs,values
        
    def createRandomBD(self,numqbits,nvalstofind):    
        nbitsindexs=int(numqbits/2)
        
        nstatesreg=  int(2** nbitsindexs)
        nregsdb =random.randint(int(nstatesreg/2),nstatesreg-1)    
        searchedlist=[]
        indexs= [0]+ random.sample(range(1,nstatesreg), nregsdb-1)
        values =[0] + random.sample(range(1,nstatesreg), nregsdb-1)
        for k in range(nvalstofind):
            searchedlist.append(values[k+1])
        self.AddTextOut("THERE ARE "+str(  nregsdb) + " RANDOM REGISTERS IN DATABASE =  ( max = " + str(nstatesreg) +  " )")
        self.AddTextOut("address = "+str( indexs))
        self.AddTextOut("values  = "+str( values))
        self.AddTextOut("search address for values = "+str( searchedlist))
        return searchedlist,indexs,values
        
    def AddTextOut(self , text):
        self.txOUT.append(text)
    def OnGroverCLick(self):
        #self.txOUT.setText(self.txNQ.text())
        #self.listOUT.addItem("2")
        if self.groverobj.stateSearch == self.groverobj.SEARCHING:            
            self.groverobj.stateSearch = self.groverobj.SEARCHCANCEL
            self.btGROVER.setText("wait...")
        elif self.groverobj.stateSearch == self.groverobj.NOSEARCHING:
            self.txOUT.setText("")
            self.btGROVER.setText("Stop")            
            self.bPurity = self.ckPUREZA.isChecked()
            if self.bUserBd:                
                self.txNQ.setText("7")
                self.txNSOLUS.setText("2")                                
                self.numqbits=7
                self.nvalstofind=2                
                searchedlist,indexs,datos=self.createUserBD(self.nvalstofind)                
            else:
                self.numqbits = int(self.txNQ.text())
                self.nvalstofind = int(self.txNSOLUS.text())                
                searchedlist,indexs,datos= self.createRandomBD(self.numqbits,self.nvalstofind)                
                
            sdb=""
            
            for k in range(len(searchedlist)):        
                meta=indexs[datos.index(searchedlist[k])]
                sdb +="search value = " + str(searchedlist[k])+ " must return address " +  str(meta) +  " ( " + binarystring(meta,int(self.numqbits/2))+" ) \n"
            self.AddTextOut(sdb)
            self.groverobj.Reset(self.numqbits,int(self.txNEXE.text() ))
            self.RunSearchThread(searchedlist,indexs,datos)            
                
    def OnMNU_BD_USER(self):
        self.MNU_BD_RAND.setChecked (False)
        self.bUserBd=True
    def OnMNU_BD_RAND(self):
        self.MNU_BD_USER.setChecked (False)
        self.bUserBd=False
    def setupUi(self, MainWindow):
        self.numqbits = 7
        self.nvalstofind=2
        self.bPurity=False
        self.bUserBd=False
        self.groverobj = Grover()
        self.thread=None
        self.worker=None
        self.dialog=None
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 544)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 20, 121, 31))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 70, 131, 51))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(230, 10, 131, 51))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(310, 40, 161, 51))
        self.label_4.setObjectName("label_4")
        self.btGROVER = QtWidgets.QPushButton(self.centralwidget)
        self.btGROVER.setGeometry(QtCore.QRect(500, 20, 111, 91))
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.btGROVER.setFont(font)
        self.btGROVER.setObjectName("btGROVER")
        self.listOUT = QtWidgets.QListWidget(self.centralwidget)
        self.listOUT.setGeometry(QtCore.QRect(30, 130, 256, 141))
        self.listOUT.setObjectName("listOUT")
        self.txOUT = QtWidgets.QTextEdit(self.centralwidget)
        self.txOUT.setGeometry(QtCore.QRect(30, 290, 661, 201))
        self.txOUT.setObjectName("txOUT")
        self.txNQ = QtWidgets.QLineEdit(self.centralwidget)
        self.txNQ.setGeometry(QtCore.QRect(140, 20, 51, 41))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txNQ.sizePolicy().hasHeightForWidth())
        self.txNQ.setSizePolicy(sizePolicy)
        self.txNQ.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.txNQ.setObjectName("txNQ")
        self.txNSOLUS = QtWidgets.QLineEdit(self.centralwidget)
        self.txNSOLUS.setGeometry(QtCore.QRect(140, 70, 31, 41))
        self.txNSOLUS.setObjectName("txNSOLUS")
        self.txNEXE = QtWidgets.QLineEdit(self.centralwidget)
        self.txNEXE.setGeometry(QtCore.QRect(230, 50, 61, 41))
        self.txNEXE.setObjectName("txNEXE")

        self.ckPUREZA = QtWidgets.QCheckBox(self.centralwidget)
        self.ckPUREZA.setObjectName("ckPUREZA")
        self.ckPUREZA.setText("Show entaglement")
        self.ckPUREZA.move(350,170)
        f = self.ckPUREZA.font()
        f.setPointSize(16) 
        self.ckPUREZA.setFont(f)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 641, 27))
        self.menubar.setObjectName("menubar")
        self.menuDatabase = QtWidgets.QMenu(self.menubar)
        self.menuDatabase.setObjectName("menuDatabase")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.MNU_BD_USER = QtWidgets.QAction(MainWindow)
        self.MNU_BD_USER.setCheckable(True)
        self.MNU_BD_USER.setObjectName("MNU_BD_USER")
        self.MNU_BD_RAND = QtWidgets.QAction(MainWindow)
        self.MNU_BD_RAND.setCheckable(True)
        self.MNU_BD_RAND.setChecked (True)
        self.MNU_BD_RAND.setObjectName("MNU_BD_RAND")        
        self.menuDatabase.addAction(self.MNU_BD_USER)
        self.menuDatabase.addAction(self.MNU_BD_RAND)
        self.menubar.addAction(self.menuDatabase.menuAction())

        self.retranslateUi(MainWindow)
        self.btGROVER.clicked.connect(self.OnGroverCLick)        
        self.MNU_BD_USER.triggered.connect(self.OnMNU_BD_USER)
        self.MNU_BD_RAND.triggered.connect(self.OnMNU_BD_RAND)        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Grover GUI"))
        self.label.setText(_translate("MainWindow", "Nº de qubits"))
        self.label_2.setText(_translate("MainWindow", "How many \n"
"values to find"))
        self.label_3.setText(_translate("MainWindow", "Execute circuit"))
        self.label_4.setText(_translate("MainWindow", "times for statistics"))
        self.btGROVER.setText(_translate("MainWindow", "Grover"))
        self.txOUT.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:14pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Info grover</p></body></html>"))
        self.txNQ.setText(_translate("MainWindow", "9"))
        self.txNSOLUS.setText(_translate("MainWindow", "2"))
        self.txNEXE.setText(_translate("MainWindow", "150"))
        self.menuDatabase.setTitle(_translate("MainWindow", "Database"))
        self.MNU_BD_USER.setText(_translate("MainWindow", "BD user fixed"))
        self.MNU_BD_RAND.setText(_translate("MainWindow", "BD random"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()    
    sys.exit(app.exec_())

