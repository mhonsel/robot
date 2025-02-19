import cv2
import numpy as np
from tflite_support.task import processor

# Constants for visualization
_MARGIN: int = 10  # Pixel margin for text placement
_ROW_SIZE: int = 10  # Pixel row spacing for text
_FONT_SIZE: int = 1  # Font size for text annotation
_FONT_THICKNESS: int = 1  # Thickness of the text font
_TEXT_COLOR: tuple[int, int, int] = (0, 0, 255)  # Red color for text and bounding boxes (BGR format)


def draw_detection_result(
    image: np.ndarray,
    detection_result: processor.DetectionResult,
) -> np.ndarray:
    """
    Draws bounding boxes and labels on the input image for detected objects.

    Args:
        image (np.ndarray): The input RGB image.
        detection_result (processor.DetectionResult): The detection result containing bounding boxes and labels.

    Returns:
        np.ndarray: The image with bounding boxes and labels drawn.
    """
    for detection in detection_result.detections:
        # Extract bounding box coordinates
        bbox = detection.bounding_box
        start_point = (bbox.origin_x, bbox.origin_y)
        end_point = (bbox.origin_x + bbox.width, bbox.origin_y + bbox.height)

        # Draw the bounding box on the image
        cv2.rectangle(image, start_point, end_point, _TEXT_COLOR, 3)

        # Extract label and confidence score
        category = detection.categories[0]
        category_name: str = category.category_name
        probability: float = round(category.score, 2)

        # Format label text
        result_text: str = f"{category_name} ({probability})"
        text_location: tuple[int, int] = (_MARGIN + bbox.origin_x, _MARGIN + _ROW_SIZE + bbox.origin_y)

        # Draw the label and confidence score on the image
        cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN, _FONT_SIZE, _TEXT_COLOR, _FONT_THICKNESS)

    return image