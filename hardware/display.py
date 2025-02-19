from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

DEFAULT_FONT = ImageFont.truetype('FreeSans.ttf', 10)
LEFT_MARGIN = 5
TOP_MARGIN = 5
LINE_HEIGHT = 12 

class Display:
    def __init__(self):
        # initialize display
        serial = i2c(port=1, address=0x3C)
        self.device = ssd1306(serial)

    def update(self, text, font=DEFAULT_FONT):
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="white", fill="black")
            for i, key in enumerate(text.keys()):
                draw.text((LEFT_MARGIN, TOP_MARGIN + i * LINE_HEIGHT), text[key], font=font, fill="white")
