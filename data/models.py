import os.path


def path(name: str) -> str:
    """
    Generates an absolute path to a model or label file within the 'models' directory.

    Args:
        name (str): The filename of the model or label file.

    Returns:
        str: The absolute path to the specified file.
    """
    root: str = os.path.dirname(os.path.realpath(__file__))  # Get directory of current script
    return os.path.join(root, "models", name)  # Construct full file path


# Image Models

# Face detection model for identifying human faces in images
FACE_DETECTION_MODEL: str = path("ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite")

# Object detection model for recognizing objects from the COCO dataset
OBJECT_DETECTION_MODEL: str = path("ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite")

# Classification model for general image classification tasks
CLASSIFICATION_MODEL: str = path("tf2_mobilenet_v2_1.0_224_ptq_edgetpu.tflite")

# Classification model for imprinting-based learning
CLASSIFICATION_IMPRINTING_MODEL: str = path("mobilenet_v1_1.0_224_l2norm_quant_edgetpu.tflite")

# Pose estimation model for detecting human poses (e.g., MoveNet)
MOVENET_MODEL: str = path("movenet_single_pose_lightning_ptq_edgetpu.tflite")


# Label Files

# Labels for image classification (ImageNet dataset)
CLASSIFICATION_LABELS: str = path("imagenet_labels.txt")

# Labels for object detection (COCO dataset)
OBJECT_DETECTION_LABELS: str = path("coco_labels.txt")


# Audio Models

# Audio classification model for recognizing voice commands
AUDIO_CLASSIFICATION_MODEL: str = path("voice_commands.tflite")