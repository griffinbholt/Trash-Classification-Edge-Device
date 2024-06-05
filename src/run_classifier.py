import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

from Classifier import Classifier

class ImageViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window properties (title and initial size)
        self.setWindowTitle("Image Viewer")
        self.setGeometry(75, 75, 300, 200)  # (x, y, width, height)

        # Create a central widget for the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a QLabel for displaying images
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create "Classify" buttons
        self.classify_button = QPushButton("Classify")

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

    def waiting_state(self):
        self.classify_button.setEnabled(True)
        self.load_image("images/classify.jpg")

    def load_image(self, image_path):
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(QApplication.primaryScreen().size(), aspectRatioMode=1) 
        self.image_label.setPixmap(scaled_pixmap)

    def scan_input(self):
        self.classify_button.setEnabled(False)
        self.load_image("images/scanning.jpg")
        self.classifier = Classifier(camera=0)  # TODO: Argument
        self.classifier.result_ready.connect(self.display_result)
        self.classifier.start()

    def display_result(self, filename):
        self.load_image(filename)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.waiting_state)
        self.timer.start(5000)


def main():
    app = QApplication(sys.argv)
    window = ImageViewerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()