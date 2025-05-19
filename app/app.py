import streamlit as st
from PIL import Image
import numpy as np
import pytesseract

def extract_text_from_image(image_path):
    input_image = Image.open(image_path)
    input_array = np.array(input_image)
    output_image = Image.fromarray(input_array)

    raw_text = pytesseract.image_to_string(output_image)
    cleaned_text = raw_text.replace("-", "").replace("=", "")
    return cleaned_text

def main():
    st.title("Image Text Extractor")
    
    # File uploader for image
    uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        image_path = "temp_image.png"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Extract text from the uploaded image
        extracted_text = extract_text_from_image(image_path)
        
        # Display the extracted text in a textarea
        st.text_area("Extracted Text", extracted_text, height=300)

if __name__ == "__main__":
    main()
