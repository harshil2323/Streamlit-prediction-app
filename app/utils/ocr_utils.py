import cv2
import numpy as np
import pytesseract
import easyocr
from PIL import Image
import streamlit as st
import os
from spellchecker import SpellChecker
import Levenshtein
import torch

# Initialize OCR engines
def init_ocr_engines():
    """
    Initialize both OCR engines and spell checker
    """
    engines = {'status': True, 'error': None}
    
    try:
        # Initialize EasyOCR
        engines['easyocr'] = easyocr.Reader(['en'])
        
        # Initialize Tesseract
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            engines['tesseract'] = True
        
        # Initialize spell checker
        engines['spellcheck'] = SpellChecker()
        
        # Check for GPU
        engines['gpu'] = torch.cuda.is_available()
        
    except Exception as e:
        engines['status'] = False
        engines['error'] = str(e)
    
    return engines

# Global OCR engines
OCR_ENGINES = init_ocr_engines()

def preprocess_image(image, options=None):
    """
    Preprocess the image for better OCR results with advanced enhancements
    """
    if options is None:
        options = {
            'grayscale': True,
            'denoise': True,
            'contrast': False,
            'contrast_level': 1.5
        }
    
    # Convert to numpy array if PIL Image
    if isinstance(image, Image.Image):
        image = np.array(image)
    
    # Make a copy to avoid modifying original
    processed = image.copy()
    
    # Convert to grayscale if needed
    if options.get('grayscale', True):
        if len(processed.shape) == 3:
            processed = cv2.cvtColor(processed, cv2.COLOR_RGB2GRAY)
    
    # Apply contrast enhancement using CLAHE
    if options.get('contrast', False):
        clahe = cv2.createCLAHE(
            clipLimit=float(options.get('contrast_level', 1.5)),
            tileGridSize=(8,8)
        )
        processed = clahe.apply(processed)
    
    # Apply bilateral filter for edge-preserving smoothing
    processed = cv2.bilateralFilter(processed, 9, 75, 75)
    
    # Apply adaptive thresholding
    processed = cv2.adaptiveThreshold(
        processed,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )
    
    # Apply noise removal if needed
    if options.get('denoise', True):
        processed = cv2.fastNlMeansDenoising(processed)
    
    # Dilate to connect text components
    kernel = np.ones((1,1), np.uint8)
    processed = cv2.dilate(processed, kernel, iterations=1)
    
    return processed

def validate_text(text, spell_checker):
    """
    Validate and correct text using spell checking
    """
    words = text.split()
    corrected_words = []
    word_confidence = []
    
    for word in words:
        if word.strip():
            # Check if word is misspelled
            if not spell_checker.known([word]):
                # Get suggestions
                candidates = spell_checker.candidates(word)
                if candidates:
                    # Find best match using Levenshtein distance
                    best_match = min(candidates, key=lambda x: Levenshtein.distance(word, x))
                    similarity = 1 - (Levenshtein.distance(word, best_match) / max(len(word), len(best_match)))
                    corrected_words.append(best_match)
                    word_confidence.append(similarity)
                else:
                    corrected_words.append(word)
                    word_confidence.append(0.5)  # Medium confidence for unknown words
            else:
                corrected_words.append(word)
                word_confidence.append(1.0)  # High confidence for known words
    
    return {
        'text': ' '.join(corrected_words),
        'word_confidence': word_confidence,
        'avg_confidence': sum(word_confidence) / len(word_confidence) if word_confidence else 0
    }

def extract_text(image, lang='eng', preprocessing_options=None, mode='Fast'):
    """
    Extract text using hybrid OCR approach
    """
    try:
        if not OCR_ENGINES['status']:
            raise RuntimeError(f"OCR engines not properly initialized: {OCR_ENGINES['error']}")
        
        # Preprocess the image
        processed_image = preprocess_image(image, preprocessing_options)
        results = {'text': '', 'confidence': 0, 'details': {}}
        
        # EasyOCR processing
        if 'easyocr' in OCR_ENGINES:
            try:
                easy_result = OCR_ENGINES['easyocr'].readtext(
                    processed_image,
                    detail=1,
                    paragraph=True
                )
                if easy_result:
                    easy_text = ' '.join([text[1] for text in easy_result])
                    easy_conf = sum([text[2] for text in easy_result]) / len(easy_result)
                    results['details']['easyocr'] = {
                        'text': easy_text,
                        'confidence': easy_conf * 100
                    }
            except Exception as e:
                st.warning(f"EasyOCR processing failed: {str(e)}")
        
        # Tesseract processing
        if OCR_ENGINES.get('tesseract'):
            try:
                custom_config = f'-l {lang} --oem 1 --psm 6' if mode == 'Accurate' else f'-l {lang} --oem 3 --psm 6'
                tess_text = pytesseract.image_to_string(processed_image, config=custom_config)
                tess_data = pytesseract.image_to_data(processed_image, config=custom_config, output_type=pytesseract.Output.DICT)
                confidences = [int(conf) for conf in tess_data['conf'] if conf != '-1']
                tess_conf = sum(confidences) / len(confidences) if confidences else 0
                results['details']['tesseract'] = {
                    'text': tess_text.strip(),
                    'confidence': tess_conf
                }
            except Exception as e:
                st.warning(f"Tesseract processing failed: {str(e)}")
        
        # Choose best result or combine results
        if 'easyocr' in results['details'] and 'tesseract' in results['details']:
            # Use result with higher confidence
            easy_conf = results['details']['easyocr']['confidence']
            tess_conf = results['details']['tesseract']['confidence']
            
            if easy_conf > tess_conf:
                results['text'] = results['details']['easyocr']['text']
                results['confidence'] = easy_conf
            else:
                results['text'] = results['details']['tesseract']['text']
                results['confidence'] = tess_conf
        elif 'easyocr' in results['details']:
            results['text'] = results['details']['easyocr']['text']
            results['confidence'] = results['details']['easyocr']['confidence']
        elif 'tesseract' in results['details']:
            results['text'] = results['details']['tesseract']['text']
            results['confidence'] = results['details']['tesseract']['confidence']
        
        # Validate and correct text
        if results['text'] and OCR_ENGINES.get('spellcheck'):
            validated = validate_text(results['text'], OCR_ENGINES['spellcheck'])
            results['text'] = validated['text']
            results['word_confidence'] = validated['word_confidence']
            results['confidence'] = (results['confidence'] + validated['avg_confidence'] * 100) / 2
        
        results['language'] = lang
        results['word_count'] = len(results['text'].split())
        
        return results
    except Exception as e:
        st.error(f"Error in OCR processing: {str(e)}")
        return None

def save_text(text, filename):
    """
    Save extracted text to a file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except Exception as e:
        st.error(f"Error saving text: {str(e)}")
        return False
