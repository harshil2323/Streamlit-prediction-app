import cv2
import numpy as np
from PIL import Image

def load_image(image_file):
    """Load an image file and return as PIL Image"""
    img = Image.open(image_file)
    return img

def get_image_details(img):
    """Get basic details about the image"""
    return {
        'format': img.format,
        'size': img.size,
        'mode': img.mode
    }

def capture_photo():
    """Capture photo from webcam"""
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert to PIL Image
        return Image.fromarray(frame)
    return None
