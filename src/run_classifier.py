import json
import shutil
import sys
import time

from picamera2 import Picamera2, Preview
from PIL import Image

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

from classifier import Classifier

class ImageViewerApp(QMainWindow):
    def __init__(self, config_file="config.json"):
        super().__init__()

        # Read in config file
        with open(config_file, "r") as file:
            config = json.load(file)

        # Load the image configurations
        self.img_dir = config["images"]["dir"]
        self.waiting_img = self.img_dir + config["images"]["waiting"]
        self.scanning_img = self.img_dir + config["images"]["scanning"]
        self.input_img = config["images"]["input"]
        self.result_display_time = config["UI"]["result_display_time"]

        # Set the window properties (title and initial size)
        self.setWindowTitle(config["UI"]["window"]["title"])
        self.setGeometry(
            config["UI"]["window"]["x"],
            config["UI"]["window"]["y"],
            config["UI"]["window"]["width"],
            config["UI"]["window"]["height"]
        )

        # Create a central widget for the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a QLabel for displaying images
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create "Classify" buttons
        self.classify_button = QPushButton(config["UI"]["button_text"])

        # Generate the waiting state
        self.waiting_state()

        # Connect button clicks to navigation methods
        self.classify_button.clicked.connect(self.camera_state)

        # Create a layout for the central widget
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.classify_button)

        # Set the layout for the central widget
        central_widget.setLayout(layout)

        # Load camera
        self.picam2 = Picamera2(camera_num=config["classifier"]["camera"])
        self.picam2.start_preview(Preview.NULL)
        cam_config = self.picam2.create_preview_configuration({
            "size": (320, 240),
            "format": "BGR888"
        })
        self.picam2.configure(cam_config)
        self.picam2.start()    

        # Initialize the Classifier
        self.classifier = Classifier(
            config=config["classifier"],
            camera=self.picam2,
            img_dir=self.img_dir,
            input_img=self.input_img
        )

    def waiting_state(self):
        self.classify_button.setEnabled(True)
        self.load_image(self.waiting_img)

    def camera_state(self):
        self.classify_button.setEnabled(False)
        start = time.time()
        while (time.time() - start < 10):
            img = Image.fromarray(self.picam2.capture_array()).resize(size=(224, 224), resample=Image.Resampling.LANCZOS)
            img.save(self.img_dir + "new_" + self.input_img)
            shutil.move(self.img_dir + "new_" + self.input_img, self.img_dir + self.input_img)
            self.load_image(self.img_dir + self.input_img)
        self.scan_input()

    def load_image(self, image_path):
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(QApplication.primaryScreen().size(), aspectRatioMode=1) 
        self.image_label.setPixmap(scaled_pixmap)

    def scan_input(self):
        self.load_image(self.scanning_img)
        self.classifier.result_ready.connect(self.display_result)
        self.classifier.start()

    def display_result(self, filename):
        self.load_image(filename)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.waiting_state)
        self.timer.start(self.result_display_time)


def main():
    app = QApplication(sys.argv)
    window = ImageViewerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()