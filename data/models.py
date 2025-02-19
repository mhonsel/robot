import os.path

def path(name):
    root = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(root, 'models', name)

# Images

# Models
FACE_DETECTION_MODEL = path('ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite')
OBJECT_DETECTION_MODEL = path('ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite')
CLASSIFICATION_MODEL = path('tf2_mobilenet_v2_1.0_224_ptq_edgetpu.tflite')
CLASSIFICATION_IMPRINTING_MODEL = path('mobilenet_v1_1.0_224_l2norm_quant_edgetpu.tflite')
MOVENET_MODEL = path('movenet_single_pose_lightning_ptq_edgetpu.tflite')

# Labels
CLASSIFICATION_LABELS = path('imagenet_labels.txt')
OBJECT_DETECTION_LABELS = path('coco_labels.txt')

# Audio

# Models
AUDIO_CLASSIFICATION_MODEL = path('voice_commands.tflite')

