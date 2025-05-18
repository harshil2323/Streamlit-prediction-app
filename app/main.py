import streamlit as st
from PIL import Image
import os
from utils.image_utils import load_image, get_image_details, capture_photo
from utils.ocr_utils import extract_text, save_text, preprocess_image
from utils.doc_utils import create_word_document, get_document_bytes

# Initialize state
if 'is_dark_theme' not in st.session_state:
    st.session_state.is_dark_theme = False

# Configure page
st.set_page_config(
    page_title="OCR Document Scanner",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Apply theme based on state
theme_styles = """
<style>
    .stButton>button {
        width: 100%;
    }
    .stTextArea textarea {
        font-size: 1rem;
        line-height: 1.5;
        background-color: var(--background-color);
        color: var(--text-color);
        border: 1px solid var(--secondary-background-color);
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stMarkdown {
        margin-bottom: 0.5rem;
    }
    </style>
"""

st.markdown(theme_styles, unsafe_allow_html=True)

# Set theme config
dark_theme = {
    "backgroundColor": "#0E1117",
    "secondaryBackgroundColor": "#262730",
    "textColor": "#FAFAFA"
}

light_theme = {
    "backgroundColor": "#FFFFFF",
    "secondaryBackgroundColor": "#F0F2F6",
    "textColor": "#262730"
}

# Apply theme
if st.session_state.is_dark_theme:
    for key, value in dark_theme.items():
        st.config.set_option(f'theme.{key}', value)
else:
    for key, value in light_theme.items():
        st.config.set_option(f'theme.{key}', value)

def main():
    # Initialize OCR status message
    st.info("Using EasyOCR engine (CPU mode)")
    
    # Header with title and theme toggle
    header_container = st.container()
    with header_container:
        col1, col2 = st.columns([6, 1])
    
    with col1:
        st.title("📄 Document Scanner")
    
    with col2:
        theme_icon = "🌙" if not st.session_state.is_dark_theme else "☀️"
        if st.button(theme_icon, help="Toggle Light/Dark Theme", use_container_width=True):
            st.session_state.is_dark_theme = not st.session_state.is_dark_theme
            # Update theme and rerun
            if st.session_state.is_dark_theme:
                for key, value in dark_theme.items():
                    st.config.set_option(f'theme.{key}', value)
            else:
                for key, value in light_theme.items():
                    st.config.set_option(f'theme.{key}', value)
            st.rerun()
    
    # Main container
    with st.container():
        st.write("Upload an image or capture using your camera")
        
        # Main content area with two columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Action buttons at the top
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("📁 Upload Image", use_container_width=True, type="primary"):
                    st.session_state.capture_mode = False
            with btn_col2:
                if st.button("📸 Capture Photo", use_container_width=True):
                    st.session_state.capture_mode = True
                    
            # Main input area
            if st.session_state.get('capture_mode', False):
                # Camera capture interface
                if st.button("Take Photo", type="primary", use_container_width=True):
                    image = capture_photo()
                    if image is not None:
                        st.image(image, caption='Captured Image', width=400)
                    else:
                        st.error("Failed to capture image. Please check your camera.")
            else:
                # File upload interface
                uploaded_file = st.file_uploader(
                    "Drop image file here",
                    type=['png', 'jpg', 'jpeg'],
                    label_visibility="collapsed"
                )
                
                if uploaded_file is not None:
                    image = load_image(uploaded_file)
                    st.image(image, caption='Uploaded Image', width=400)

        # Show image details and OCR controls in the side column
        with col2:
            if 'image' in locals():
                with st.container():
                    # Image Details
                    st.subheader("Image Details")
                    details = get_image_details(image)
                    st.write(f"Format: {details['format']}")
                    st.write(f"Size: {details['size'][0]}x{details['size'][1]}")
                    st.write(f"Mode: {details['mode']}")
                    
                    st.markdown("---")
                    
                    # Image Processing Options
                    st.subheader("Image Processing")
                    with st.expander("Preprocessing Options"):
                        apply_grayscale = st.checkbox("Convert to Grayscale", value=True)
                        apply_denoise = st.checkbox("Remove Noise", value=True)
                        apply_contrast = st.checkbox("Enhance Contrast", value=False)
                        if apply_contrast:
                            contrast_level = st.slider("Contrast Level", 1.0, 3.0, 1.5, 0.1)

                    # OCR Controls
                    st.subheader("OCR Settings")
                    lang = st.selectbox(
                        "Language",
                        ["eng", "fra", "deu", "spa", "hin"],
                        format_func=lambda x: {
                            "eng": "English",
                            "fra": "French",
                            "deu": "German",
                            "spa": "Spanish",
                            "hin": "Hindi"
                        }[x]
                    )

                    # OCR Mode
                    ocr_mode = st.radio(
                        "OCR Mode",
                        ["Fast", "Accurate"],
                        horizontal=True,
                        help="Fast mode is quicker but may be less accurate"
                    )
                    
                    if st.button("Extract Text 🔍", type="primary", use_container_width=True):
                        with st.spinner("Processing image..."):
                            # Prepare preprocessing options
                            preprocessing_options = {
                                'grayscale': apply_grayscale,
                                'denoise': apply_denoise,
                                'contrast': apply_contrast,
                                'contrast_level': contrast_level if apply_contrast else 1.0
                            }
                            
                            # Process image with selected options
                            result = extract_text(
                                image,
                                lang=lang,
                                preprocessing_options=preprocessing_options,
                                mode=ocr_mode
                            )
                            
                            if result:
                                # Show original and processed images side by side
                                st.markdown("#### Image Comparison")
                                img_col1, img_col2 = st.columns(2)
                                with img_col1:
                                    st.markdown("**Original**")
                                    st.image(image, width=200)
                                with img_col2:
                                    st.markdown("**Processed**")
                                    processed_img = preprocess_image(image, preprocessing_options)
                                    st.image(processed_img, width=200)
                                st.subheader("Extracted Text")
                                
                                # Show detailed stats
                                st.markdown("#### Recognition Details")
                                stats_col1, stats_col2, stats_col3 = st.columns(3)
                                with stats_col1:
                                    st.metric("Overall Confidence", f"{result['confidence']:.1f}%")
                                with stats_col2:
                                    st.metric("Words", result['word_count'])
                                with stats_col3:
                                    if result.get('details'):
                                        engines_used = len(result['details'])
                                        st.metric("OCR Engines Used", engines_used)
                                
                                # Show engine-specific results
                                if result.get('details'):
                                    with st.expander("OCR Engine Details"):
                                        for engine, data in result['details'].items():
                                            st.markdown(f"**{engine.upper()}**")
                                            st.write(f"Confidence: {data['confidence']:.1f}%")
                                            st.text(data['text'])
                                            st.markdown("---")
                                
                                # Show word confidence if available
                                if result.get('word_confidence'):
                                    with st.expander("Word Confidence Scores"):
                                        words = result['text'].split()
                                        for word, conf in zip(words, result['word_confidence']):
                                            color = "#00ff00" if conf > 0.8 else "#ffff00" if conf > 0.5 else "#ff0000"
                                            st.markdown(f"<span style='color:{color}'>{word}</span> ({conf:.2f})", unsafe_allow_html=True)
                                
                                # Text Editor Section
                                st.markdown("### Edit Text")
                                
                                # Initialize session state for editor content
                                if 'editor_content' not in st.session_state:
                                    st.session_state.editor_content = result['text']

                                # Text editor with custom styling
                                st.markdown("""
                                    <style>
                                    .stTextArea textarea {
                                        font-size: 1rem;
                                        line-height: 1.5;
                                    }
                                    </style>
                                """, unsafe_allow_html=True)
                                
                                edited_text = st.text_area(
                                    "Edit extracted text",
                                    value=st.session_state.editor_content,
                                    height=300,
                                    key="text_editor"
                                )
                                
                                # Update session state
                                st.session_state.editor_content = edited_text

                                # Document Export Options
                                st.markdown("---")
                                st.subheader("Document Settings")
                                col1, col2 = st.columns(2)
                                with col1:
                                    font_name = st.selectbox(
                                        "Font",
                                        ["Calibri", "Arial", "Times New Roman"]
                                    )
                                with col2:
                                    font_size = st.number_input(
                                        "Font Size",
                                        min_value=8,
                                        max_value=16,
                                        value=11
                                    )

                                # Export Actions
                                st.markdown("---")
                                action_col1, action_col2 = st.columns(2)
                                with action_col1:
                                    if st.button("📋 Copy Text", use_container_width=True):
                                        st.code(edited_text)
                                        st.success("Text copied to clipboard!")
                                with action_col2:
                                    # Create and offer Word document for download
                                    doc = create_word_document(
                                        edited_text,
                                        font_name=font_name,
                                        font_size=font_size
                                    )
                                    if doc:
                                        doc_bytes = get_document_bytes(doc)
                                        if doc_bytes:
                                            st.download_button(
                                                "📥 Download as Word",
                                                doc_bytes,
                                                "extracted_document.docx",
                                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                                use_container_width=True
                                            )

if __name__ == "__main__":
    main()
