from PIL import Image
from time import sleep
from waste import WasteDestination

if __name__ == "__main__":
    for dest in WasteDestination:
        img = Image.open(dest.image())
        img.save(WasteDestination.recommended())
        sleep(2)