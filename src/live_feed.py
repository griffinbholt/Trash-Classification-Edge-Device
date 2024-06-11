import numpy as np
import time

from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

class LiveFeed(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, picam2, size, time):
        super().__init__()
        self.picam2 = picam2
        self.size = size
        self.time = int(time / 1000)

    def run(self):
        self.start_time = time.time()
        self.ThreadActive = True
        while self.ThreadActive:
            img = Image.fromarray(self.picam2.capture_array()).resize(size=(224, 224), resample=Image.Resampling.LANCZOS)
            
            draw = ImageDraw.Draw(img)
            font_size = 100
            try:
                font = ImageFont.truetype("Piboto-Bold.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
            text = str(int(self.time - (time.time() - self.start_time)) + 1)
            text_width, text_height = draw.textsize(text, font=font)
            position = ((224 - text_width) // 2, ((224 - text_height) // 2) - 20)
            draw.text(position, text, fill=(255, 255, 255), font=font)

            font_size = 11
            try:
                font = ImageFont.truetype("Piboto-Bold.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
            text = "Place item in front of the camera."
            text_width, text_height = draw.textsize(text, font=font)
            position = ((224 - text_width) // 2, ((224 - text_height) // 2) - 100)
            draw.text(position, text, fill=(255, 255, 255), font=font)

            ConvertToQtFormat = QImage(np.array(img).data, 224, 224, QImage.Format_RGB888)
            Pic = ConvertToQtFormat.scaled(600, 600)
            self.ImageUpdate.emit(Pic)
        # Load clean image
        img = Image.fromarray(self.picam2.capture_array()).resize(size=(224, 224), resample=Image.Resampling.LANCZOS)
        ConvertToQtFormat = QImage(np.array(img).data, 224, 224, QImage.Format_RGB888)
        Pic = ConvertToQtFormat.scaled(600, 600)
        self.ImageUpdate.emit(Pic)

    def stop(self):
        self.ThreadActive = False
        self.quit()
