from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer, QMetaObject, pyqtSignal
import os
import win32gui
import win32con

from ansi import ansi

class ScreenshotOverlay(QWidget):
    activate_signal = pyqtSignal(str)  # Emitting the image path
    deactivate_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.activate_signal.connect(self.activate_overlay)
        self.deactivate_signal.connect(self.deactivate_overlay)

        print(ansi.OKCYAN + "[Overlay] Initializing ScreenshotOverlay..." + ansi.ENDC)

        # Setup the overlay window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # Click-through
        self.setGeometry(QApplication.primaryScreen().geometry())  # Full-screen overlay
        print(ansi.OKCYAN + "[Overlay] Overlay geometry set:", self.geometry(), ansi.ENDC)

        # Label to display screenshot
        self.label = QLabel(self)
        self.label.setGeometry(self.rect())
        self.label.setScaledContents(True)  # Ensures the image is displayed properly
        print(ansi.OKCYAN + "[Overlay] QLabel initialized." + ansi.ENDC)

        # Initially hidden
        self.hide()
        print(ansi.OKCYAN + "[Overlay] Initialized successfully, currently hidden." + ansi.ENDC)

    def activate_overlay(self, screenshot_path):
        """Shows the overlay with a given screenshot"""
        print(ansi.OKCYAN + f"[Overlay] Activating overlay with screenshot: {screenshot_path}" + ansi.ENDC)

        if not os.path.exists(screenshot_path):
            print(ansi.FAIL + "[ERROR] Screenshot file not found:", screenshot_path, ansi.ENDC)
            return

        pixmap = QPixmap(screenshot_path)
        if pixmap.isNull():
            print(ansi.FAIL + "[ERROR] Failed to load screenshot into QPixmap" + ansi.ENDC)
            return

        self.label.setPixmap(pixmap)
        self.label.adjustSize()  # Adjusts the label size to fit the image

        self.setWindowOpacity(0.99)
        self.show()
        print(ansi.OKCYAN + "[Overlay] Overlay set to visible:", self.isVisible(), ansi.ENDC)

        self.raise_()  # Bring it to the front
        self.update()   # Force UI update
        print(ansi.OKCYAN + "[Overlay] Overlay raised and updated." + ansi.ENDC)

        hwnd = int(self.winId())
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

    def deactivate_overlay(self):
        """Hides the overlay"""
        print(ansi.OKCYAN + "[Overlay] Deactivating overlay." + ansi.ENDC)
        self.hide()
        print(ansi.OKCYAN + "[Overlay] Overlay is now hidden." + ansi.ENDC)
