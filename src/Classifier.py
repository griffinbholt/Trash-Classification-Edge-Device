import numpy as np
import shutil
import time
import tflite_runtime.interpreter as tflite

from picamera2 import Picamera2, Preview
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal
from waste import WasteClass, WasteDestination

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

        # Load the model
        self.interpreter = tflite.Interpreter(
            model_path="models/trash_classifier_v0.tflite", # TODO: Create argument
            num_threads=2 # TODO: Create argument
        )
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.floating_model = self.input_details[0]["dtype"] == np.float32

        # N x H x W x C, H:1, W:2
        self.height = self.input_details[0]["shape"][1]
        self.width = self.input_details[0]["shape"][2]

    def run(self):
        # Retrieve image
        img = Image.fromarray(self.picam2.capture_array()).resize(size=(self.width, self.height), resample=Image.Resampling.LANCZOS)

        # Save input
        img.save("images/new_input.png")
        shutil.move("images/new_input.png", "images/input.png")

        # Add N dim
        input_data = np.expand_dims(img, axis=0)

        if self.floating_model:
            input_data = (np.float32(input_data) - 0.0) / 255.0 
        
        self.interpreter.set_tensor(self.input_details[0]["index"], input_data)

        start_time = time.time()
        self.interpreter.invoke()
        stop_time = time.time()

        output_data = self.interpreter.get_tensor(self.output_details[0]["index"])
        results = np.squeeze(output_data)

        top_k = results.argsort()[-5:][::-1]

        for i in top_k:
            if self.floating_model:
                print("{:08.6f}: {}".format(float(results[i]), WasteClass(i)))
            else:
                print("{:08.6f}: {}".format(float(results[i] / 255.0), WasteClass(i)))

        print("time: {:.3f}ms".format((stop_time - start_time) * 1000))

        self.result_ready.emit("images/Recycle.jpg")