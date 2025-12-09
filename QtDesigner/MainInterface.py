# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os

from QtDesigner.Airline_Settings import MainWindow as Settings


class AirplaneItem(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.setPixmap(QtGui.QPixmap(
            "images/ready_take_off-removebg.png"
        ))
        self.setScaledContents(True)

        self.resize(600, 400)

        self.base_pos = QtCore.QPoint(0, 0)

        self.anim = QtCore.QPropertyAnimation(self, b"pos")
        self.anim.setDuration(220)

        # New properties for takeoff animation
        self.is_flying = False
        self.original_pixmap = QtGui.QPixmap("images/ready_take_off-removebg.png")
        self.takeoff_anim_group = None

    def enterEvent(self, e):
        self.anim.stop()
        self.anim.setEndValue(self.base_pos - QtCore.QPoint(0, 40))
        self.anim.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.anim.stop()
        self.anim.setEndValue(self.base_pos)
        self.anim.start()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        self.clicked.emit()
        e.accept()
        super().mousePressEvent(e)

    def triggerTakeoff(self):
        """Public method to trigger plane animation"""
        print("Triggering plane takeoff...")
        if hasattr(self, 'plane') and hasattr(self.plane, 'startTakeoff'):
            self.plane.startTakeoff()
        else:
            print("ERROR: Plane or startTakeoff method not found!")
    def startTakeoff(self):
        if self.is_flying:
            return

        self.is_flying = True

        # Disable hover effect during flight
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

        parent_center_x = self.parent().width() // 2 - self.width() // 2
        target_pos = QtCore.QPoint(parent_center_x, -self.height())

        # Create rotation animation (45° during ascent)
        rotation_anim = QtCore.QVariantAnimation()
        rotation_anim.setDuration(1500)
        rotation_anim.setStartValue(0)
        rotation_anim.setEndValue(-45)
        rotation_anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)

        # Connect rotation animation to apply rotation
        rotation_anim.valueChanged.connect(self.applyRotation)

        # Create movement animation to top center
        move_anim = QtCore.QPropertyAnimation(self, b"pos")
        move_anim.setDuration(3000)
        move_anim.setStartValue(self.pos())
        move_anim.setEndValue(target_pos)
        move_anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)

        # Create parallel animation group for simultaneous movement and rotation
        self.takeoff_anim_group = QtCore.QParallelAnimationGroup()
        self.takeoff_anim_group.addAnimation(rotation_anim)
        self.takeoff_anim_group.addAnimation(move_anim)

        # When ascent is complete, rotate back to 0°
        self.takeoff_anim_group.finished.connect(self.rotateBackToZero)

        # Start the animation
        self.takeoff_anim_group.start()

    def rotateBackToZero(self):
        # Create rotation back animation
        rotation_back_anim = QtCore.QVariantAnimation()
        rotation_back_anim.setDuration(1000)
        rotation_back_anim.setStartValue(45)
        rotation_back_anim.setEndValue(0)
        rotation_back_anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)

        # Connect to apply rotation
        rotation_back_anim.valueChanged.connect(self.applyRotation)

        # When rotation back is complete, reset state
        rotation_back_anim.finished.connect(self.onTakeoffComplete)

        # Start rotation back animation
        rotation_back_anim.start()

    def applyRotation(self, angle):
        pixmap = self.original_pixmap
        transform = QtGui.QTransform().rotate(angle)
        rotated_pixmap = pixmap.transformed(transform, QtCore.Qt.SmoothTransformation)
        self.setPixmap(rotated_pixmap)

    def onTakeoffComplete(self):
        self.is_flying = False
        # Re-enable hover effect
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        print("Takeoff animation complete!")


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1001, 650)

        self.central = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.central)

        # BACKGROUND
        self.background = QtWidgets.QLabel(self.central)
        self.background.setGeometry(0, 0, 1001, 650)
        self.background.setScaledContents(True)
        self.background.setPixmap(
            QtGui.QPixmap("images/sea.jpg")
        )

        # CLIFF
        self.cliff = QtWidgets.QLabel(self.central)
        self.cliff.setPixmap(
            QtGui.QPixmap("images/cliff-removebg-.png")
        )
        self.cliff.setScaledContents(True)
        self.cliff.resize(1500, 900)

        # PLANE
        self.plane = AirplaneItem(self.central)

        # Store reference to the main window instance
        self.main_window = MainWindow

        # Connect plane click to open settings
        self.plane.clicked.connect(self.openSettings)

        MainWindow.resizeEvent = self.resizeEvent
        self.updatePositions()

    def updatePositions(self):
        cliff_y = self.central.height() - self.cliff.height()
        self.cliff.move(5, cliff_y)

        plane_x = 50
        plane_y = cliff_y - self.plane.height()

        self.plane.base_pos = QtCore.QPoint(plane_x, plane_y)
        self.plane.move(self.plane.base_pos)

    def openSettings(self):
        self.settings = Settings()
        self.settings.show()

    def triggerTakeoff(self):
        """Public method to trigger the takeoff animation from outside"""
        self.plane.startTakeoff()

    def resizeEvent(self, event):
        self.background.resize(self.central.size())
        self.updatePositions()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    win = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(win)

    win.show()
    sys.exit(app.exec_())