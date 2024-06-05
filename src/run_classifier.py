import json
import sys

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
        input_img = config["images"]["input"]
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
        self.classify_button.clicked.connect(self.scan_input)

        # Create a layout for the central widget
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.classify_button)

        # Set the layout for the central widget
        central_widget.setLayout(layout)

        # Initialize the Classifier
        self.classifier = Classifier(
            config=config["classifier"],
            img_dir=self.img_dir,
            input_img=input_img
        )

    def waiting_state(self):
        self.classify_button.setEnabled(True)
        self.load_image(self.waiting_img)

    def load_image(self, image_path):
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(QApplication.primaryScreen().size(), aspectRatioMode=1) 
        self.image_label.setPixmap(scaled_pixmap)

    def scan_input(self):
        self.classify_button.setEnabled(False)
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