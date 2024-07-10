# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/gui/main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 300)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.formatLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.formatLineEdit.setObjectName("formatLineEdit")
        self.verticalLayout.addWidget(self.formatLineEdit)
        self.getTimeButton = QtWidgets.QPushButton(self.centralwidget)
        self.getTimeButton.setObjectName("getTimeButton")
        self.verticalLayout.addWidget(self.getTimeButton)
        self.newTimeLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.newTimeLineEdit.setObjectName("newTimeLineEdit")
        self.verticalLayout.addWidget(self.newTimeLineEdit)
        self.setTimeButton = QtWidgets.QPushButton(self.centralwidget)
        self.setTimeButton.setObjectName("setTimeButton")
        self.verticalLayout.addWidget(self.setTimeButton)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.getTimeButton.clicked.connect(MainWindow.handleGetTimeButtonClicked) # type: ignore
        self.setTimeButton.clicked.connect(MainWindow.handleSetTimeButtonClicked) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "Network Clock"))
        self.formatLineEdit.setPlaceholderText(_translate("MainWindow", "Enter format string"))
        self.getTimeButton.setText(_translate("MainWindow", "Get Time"))
        self.newTimeLineEdit.setPlaceholderText(_translate("MainWindow", "Enter new system time (YYYY-MM-DD HH:MM:SS)"))
        self.setTimeButton.setText(_translate("MainWindow", "Set Time"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
