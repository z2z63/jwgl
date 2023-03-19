# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'windowsoGdJi.ui'
##
## Created by: Qt User Interface Compiler version 5.15.7
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore

from PySide6.QtWebEngineWidgets import QWebEngineView



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1100, 800)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.course_table = QTableWidget(self.centralwidget)
        if (self.course_table.columnCount() < 1):
            self.course_table.setColumnCount(1)
        __qtablewidgetitem = QTableWidgetItem()
        self.course_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        self.course_table.setObjectName(u"course_table")
        self.course_table.setGeometry(QRect(0, 0, 300, 500))
        self.course_table.horizontalHeader().setDefaultSectionSize(300)
        self.console = QPlainTextEdit(self.centralwidget)
        self.console.setObjectName(u"console")
        self.console.setGeometry(QRect(300, 400, 800, 400))
        self.console.setReadOnly(True)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(0, 500, 300, 300))
        self.podium_webview = QWebEngineView(self.centralwidget)
        self.podium_webview.setObjectName(u"podium_webview")
        self.podium_webview.setEnabled(True)
        self.podium_webview.setGeometry(QRect(300, 0, 800, 400))
        self.podium_webview.setBaseSize(QSize(0, 0))
        self.podium_webview.setUrl(QUrl(u"about:blank"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1100, 35))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        ___qtablewidgetitem = self.course_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"\u8bfe\u7a0b\u540d\u79f0", None));
        self.label.setText("")
    # retranslateUi

