from enum import Enum

class WasteClass(Enum):
    """
    The classes that are currently classified by our classification algorithm
    """
    BATTERY = 1
    BIOLOGICAL = 2
    CARDBOARD = 3
    CLOTHES = 4
    GLASS = 5
    METAL = 6
    PAPER = 7
    PLASTIC = 8
    SHOES = 9
    TRASH = 10

WASTE_DEST_IMG_DIR = "images"

class WasteDestination(Enum):
    """
    The waste destinations we currently cover
    """
    ELECTRONICS_RECYCLING_CENTER = 1
    COMPOST = 2
    RECYCLE = 3
    LANDFILL = 4

    def image(self):
        images = {
            WasteDestination.ELECTRONICS_RECYCLING_CENTER: "Electronics_Recycling_Center.jpg",
            WasteDestination.COMPOST: "Compost.jpg",
            WasteDestination.RECYCLE: "Recycle.jpg",
            WasteDestination.LANDFILL: "Landfill.jpg"
        }
        return WASTE_DEST_IMG_DIR + "/" + images[self]

    @staticmethod
    def recommended():
        return WASTE_DEST_IMG_DIR + "/recommended.jpg"
