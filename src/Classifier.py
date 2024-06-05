from picamera2 import Picamera2, Preview
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal

class Classifier(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, camera):
        super().__init__()

        # Load the camera
        self.picam2 = Picamera2(camera_num=camera)
        self.picam2.start_preview(Preview.NULL)
        config = self.picam2.create_preview_configuration({
            "size": (320, 240),
            "format": "BGR888"
        })
        self.picam2.configure(config)
        self.picam2.start()

        # TODO: Load the model

    def run(self):
        # img = Image.fromarray(self.picam2.capture_array())
        # img.save("new_" + )
        # TODO - Process images
        self.result_ready.emit("images/Recycle.jpg")