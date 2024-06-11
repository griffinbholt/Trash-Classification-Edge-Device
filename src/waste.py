from enum import Enum

class WasteClass(Enum):
    """
    The classes that are currently classified by our classification algorithm
    """
    BATTERY = 0
    BIOLOGICAL = 1
    CARDBOARD = 2
    CLOTHES = 3
    GLASS = 4
    METAL = 5
    PAPER = 6
    PLASTIC = 7
    SHOES = 8
    TRASH = 9

class WasteDestination(Enum):
    """
    The waste destinations we currently cover
    """
    ELECTRONICS_RECYCLING_CENTER = 0
    COMPOST = 1
    RECYCLE = 2
    LANDFILL = 3

    def image(self):
        images = {
            WasteDestination.ELECTRONICS_RECYCLING_CENTER: "Electronics_Recycling_Center.jpg",
            WasteDestination.COMPOST: "Compost.jpg",
            WasteDestination.RECYCLE: "Recycle.jpg",
            WasteDestination.LANDFILL: "Landfill.jpg"
        }
        return images[self]
