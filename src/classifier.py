import numpy as np
import shutil
import time
import tflite_runtime.interpreter as tflite

from picamera2 import Picamera2, Preview
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal

from ruleset import Ruleset
from waste import WasteClass, WasteDestination

class Classifier(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, config, img_dir, input_img):
        super().__init__()

        # Load the camera
        self.picam2 = Picamera2(camera_num=config["camera"])
        self.picam2.start_preview(Preview.NULL)
        cam_config = self.picam2.create_preview_configuration({
            "size": (320, 240),
            "format": "BGR888"
        })
        self.picam2.configure(cam_config)
        self.picam2.start()

        # Load the model
        self.interpreter = tflite.Interpreter(
            model_path=config["model_path"],
            num_threads=config["n_threads"]
        )
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.floating_model = self.input_details[0]["dtype"] == np.float32 # True, for v0 model

        # N x H x W x C, H:1, W:2
        self.height = self.input_details[0]["shape"][1]
        self.width = self.input_details[0]["shape"][2]

        self.n_samples = config["n_samples"]
        self.img_dir = img_dir
        self.input_img = input_img

        # Load the ruleset
        self.ruleset = Ruleset.from_json(config["ruleset"])

    def run(self):
        votes = np.zeros(self.n_samples).astype(int)
        for i in range(self.n_samples):
            # Retrieve image
            img = Image.fromarray(self.picam2.capture_array()).resize(size=(self.width, self.height), resample=Image.Resampling.LANCZOS)

            # Save input
            if i == self.n_samples - 1:
                img.save(self.img_dir + "new_" + self.input_img)
                shutil.move(self.img_dir + "new_" + self.input_img, self.img_dir + self.input_img)

            # Prep input
            input_data = np.expand_dims(img, axis=0) # Add N dim
            if self.floating_model:
                input_data = (np.float32(input_data) - 0.0) / 255.0 
        
            # Process input & record class
            self.interpreter.set_tensor(self.input_details[0]["index"], input_data)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(self.output_details[0]["index"])
            results = np.squeeze(output_data)
            votes[i] = results.argmax()

        waste_class = WasteClass(np.bincount(votes).argmax())
        waste_destination = self.ruleset(waste_class)

        print("Waste Class: ", str(waste_class))
        print("Waste Destination: ", str(waste_destination), "\n")

        self.result_ready.emit(self.img_dir + waste_destination.image())