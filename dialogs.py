from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

class Ui_Settings(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Settings")
        r1 = QtCore.QRect(0, 0, 100, 100)
        Dialog.resize(640, 280)
        # Dialog.setStyleSheet("background-color: rgb(255,0,0); margin:5px; border:1px solid rgb(0, 255, 0); ")
        Dialog.setStyleSheet("margin:5px; border:1px dotted rgb(0, 0, 0); ")
        pal = QtGui.QPalette()
        pal.setColor(Dialog.backgroundRole(), Qt.white)
        # Dialog.setPalette(pal)

        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.dialoglabel1 = QtWidgets.QLabel(Dialog)
        self.dialoglabel2 = QtWidgets.QLabel(Dialog)
        self.dialoglabel3 = QtWidgets.QLabel(Dialog)
        self.dialoglabel4 = QtWidgets.QLabel(Dialog)

        self.dialoglabel1.setObjectName("dialoglabel")
        self.dialoglabel2.setObjectName("dialoglabel")
        self.dialoglabel3.setObjectName("dialoglabel")
        self.dialoglabel4.setObjectName("dialoglabel")

        self.horizontalLayout_3.addWidget(self.dialoglabel1)
        self.horizontalLayout_3.addWidget(self.dialoglabel2)
        self.horizontalLayout_3.addWidget(self.dialoglabel3)
        self.horizontalLayout_3.addWidget(self.dialoglabel4)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.dialoglineedit = QtWidgets.QLineEdit(Dialog)
        self.dialoglineedit.setObjectName("dialoglineedit")

        self.horizontalLayout_2.addWidget(self.dialoglineedit)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.cancel = QtWidgets.QPushButton(Dialog)
        self.cancel.setObjectName("cancel")
        self.horizontalLayout.addWidget(self.cancel)

        self.update = QtWidgets.QPushButton(Dialog)
        self.update.setObjectName("update")
        self.horizontalLayout.addWidget(self.update)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Settings"))

        # self.dialoglabel1.setText(_translate("Dialog", "System Settings 1 "))
        # self.dialoglabel2.setText(_translate("Dialog", "System Settings 2"))
        # self.dialoglabel3.setText(_translate("Dialog", "System Settings 3"))
        # self.dialoglabel4.setText(_translate("Dialog", "System Settings 4"))


        self.cancel.setText(_translate("Dialog", "Cancel"))
        self.update.setText(_translate("Dialog", "Update"))

