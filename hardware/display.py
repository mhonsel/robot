from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont
from typing import Dict

# Default font for display text
DEFAULT_FONT: ImageFont.FreeTypeFont = ImageFont.truetype("FreeSans.ttf", 10)

# Display layout constants
LEFT_MARGIN: int = 5  # Margin from the left edge
TOP_MARGIN: int = 5  # Margin from the top edge
LINE_HEIGHT: int = 12  # Spacing between lines of text


class Display:
    """
    Handles interactions with an SSD1306 OLED display.
    """

    def __init__(self) -> None:
        """
        Initializes the SSD1306 display using I2C communication.
        """
        serial = i2c(port=1, address=0x3C)  # Initialize I2C communication
        self.device = ssd1306(serial)  # Create the SSD1306 display object

    def update(self, text: Dict[str, str], font: ImageFont.FreeTypeFont = DEFAULT_FONT) -> None:
        """
        Updates the display with the provided text.

        Args:
            text (Dict[str, str]): Dictionary where keys are labels and values are text strings to display.
            font (ImageFont.FreeTypeFont, optional): Font to use for rendering the text. Defaults to `DEFAULT_FONT`.
        """
        with canvas(self.device) as draw:
            # Clear the screen by drawing a black rectangle
            draw.rectangle(self.device.bounding_box, outline="white", fill="black")

            # Display each line of text at the correct vertical position
            for i, key in enumerate(text.keys()):
                draw.text(
                    (LEFT_MARGIN, TOP_MARGIN + i * LINE_HEIGHT),
                    text[key],
                    font=font,
                    fill="white",
                )