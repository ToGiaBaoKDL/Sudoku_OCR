import streamlit as st
from datetime import datetime as dt
from PIL import Image
import numpy as np
import cv2
from streamlit_paste_button import paste_image_button

class PasteImageButton:
    def __init__(self, image_data=None):
        self.image_data = image_data

def paste_image_button(label, text_color, background_color, hover_background_color):
    """Custom component for pasting images from clipboard"""
    # This is a placeholder for the actual paste functionality
    # In a real implementation, you would need to use JavaScript to handle clipboard events
    return PasteImageButton()

async def enhance_image(image):
    """Enhance image for better grid detection"""
    # Convert PIL Image to numpy array
    img_array = np.array(image)
    
    # Apply basic sharpening
    kernel = np.array([[-1,-1,-1], 
                      [-1, 9,-1],
                      [-1,-1,-1]])
    sharpened = cv2.filter2D(img_array, -1, kernel)
    
    return Image.fromarray(sharpened) 