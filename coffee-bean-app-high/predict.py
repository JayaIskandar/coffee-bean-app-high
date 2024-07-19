import os
import streamlit as st
from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode, RTCConfiguration

from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import tempfile

# Set the working directory to the script's directory
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, 'best-nano.pt')
css_path = os.path.join(base_dir, 'style.css')
html_path = os.path.join(base_dir, 'predict.html')

pdf_icon_path = os.path.join(base_dir, 'pdf-icon-fix.png')

# Load CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load HTML
def load_html(file_name):
    with open(file_name) as f:
        st.markdown(f.read(), unsafe_allow_html=True)

load_css(css_path)
load_html(html_path)

# Debugging: Check if the file exists
if os.path.exists(model_path):
    st.write(f"File found at {model_path}")
else:
    st.write(f"File not found at {model_path}")

# Load the YOLOv8 model
model = YOLO(model_path)

# Confidence threshold for considering the detected object as a coffee bean
CONFIDENCE_THRESHOLD = 0.5

def load_image(image_file):
    img = Image.open(image_file)
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)  # Convert PIL image to OpenCV format

    # Calculate target size and padding color
    target_width = 300
    target_height = 300
    pad_color = (128, 128, 128)  # Gray color padding

    # Resize and pad the image
    img = resize_with_padding(img, target_width, target_height, pad_color, scale_factor=0.25)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert back to RGB format
    return img

def resize_with_padding(img, target_width, target_height, pad_color=(255, 255, 255), scale_factor=1.0):
    # Get the image dimensions
    height, width = img.shape[:2]

    # Calculate the aspect ratio
    aspect_ratio = width / height

    # Calculate the new dimensions while maintaining the aspect ratio
    if aspect_ratio > 1:
        new_width = int(target_width * scale_factor)
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = int(target_height * scale_factor)
        new_width = int(new_height * aspect_ratio)

    # Resize the image
    resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Create a new image with the target dimensions and the specified padding color
    padded_img = np.full((target_height, target_width, 3), pad_color, dtype=np.uint8)

    # Calculate the offsets for centering the resized image
    y_offset = (target_height - new_height) // 2
    x_offset = (target_width - new_width) // 2

    # Copy the resized image to the center of the padded image
    padded_img[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_img

    return padded_img

def detect_objects(_img):
    results = model.predict(source=_img, save=False)
    return results

class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.model = YOLO(model_path)  # Initialize YOLO model here

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        results = detect_objects(img)
        if results[0].boxes.data.tolist():  # Check if any objects were detected
            for result in results[0].boxes.data.tolist():
                confidence = result[4]  # Confidence score
                if confidence > 0.6:  # Adjust threshold as needed
                    class_name = self.model.names[int(result[5])]
                    x1, y1, x2, y2 = int(result[0]), int(result[1]), int(result[2]), int(result[3])  # Bounding box coordinates

                    # Draw bounding box and label on the image
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw bounding box
                    label = f"{class_name} {confidence:.2f}"  # Label with class name and confidence score
                    cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36, 255, 12), 2)  # Draw label

        return img

#################### FOR CREATING THE CONTENT OF PDF FILE ##################################
def create_pdf(test_input_path, test_output_path, predicted_class, confidence):
    class PDF(FPDF):
        def header(self):
            # Brown bar at the top
            self.set_fill_color(139, 69, 19)  # Dark brown color
            self.rect(0, 0, 210, 15, 'F')

        def footer(self):
            # Brown bar at the bottom
            self.set_fill_color(139, 69, 19)  # Dark brown color
            self.rect(0, 282, 210, 15, 'F')
            self.set_y(-40)  # Move to the bottom of the page
            self.set_font("Arial", 'I', size=8)
            self.multi_cell(0, 10, "Disclaimer: This prediction is based on machine learning models and may not be 100% accurate.", align='C')
        
        
    pdf = PDF()
    pdf.add_page()


    # Title
    pdf.set_font("Arial", 'B', size=24)
    pdf.set_text_color(139, 69, 19)  # Dark brown color
    pdf.cell(200, 30, txt="BEANXPERT", ln=True, align='C')

    # Test time
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)  # Black color
    test_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pdf.cell(200, 10, txt=f"TEST TIME: {test_time}", ln=True, align='C')

    # Test input and output photos
    pdf.set_font("Arial", 'B', size=14)
    image_width = 45  # 90 * 0.8 = 72
    pdf.cell(95, 10, txt="TEST INPUT PHOTO:", ln=0, align='L')
    pdf.cell(95, 10, txt="TEST OUTPUT PHOTO:", ln=1, align='R')
    pdf.image(test_input_path, x=10, y=70, w=image_width)
    pdf.image(test_output_path, x=150, y=70, w=image_width)

    # Test result
    pdf.ln(100)  # Move cursor down to avoid overlapping
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"TEST RESULT: This is a {predicted_class} coffee bean with confidence {confidence:.2f}", align='C')

    # Signature
    pdf.ln(10)
    pdf.cell(140)  # Move to the right
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, "Signed by BeanXpert", ln=True, align='R')

    signature_path = os.path.join(base_dir, 'signature-bean.png')
    pdf.image(signature_path, x=150, y=pdf.get_y(), w=50)  # Adjust width as needed

    pdf.ln(30)
    pdf.cell(0, 10, "Jaya Iskandar", ln=True, align='R')
    pdf.cell(0, 10, "Founder of BeanXpert", ln=True, align='R')


    # Save the PDF to a file
    pdf_file = os.path.join(base_dir, 'prediction_result.pdf')
    pdf.output(pdf_file)

    return pdf_file
#################### FOR CREATING THE CONTENT OF PDF FILE ##################################


def show_predict_page():
    st.markdown("<div class='upload-section'>Upload an image</div>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = load_image(uploaded_file)
        st.image(image, caption='Uploaded Image', width=300)  # Set width to 300 pixels

        with st.spinner("Detecting objects..."):
            results = detect_objects(image)

        is_coffee_bean = False
        max_confidence = 0.0
        predicted_class = None

        if results[0].boxes.data.tolist():  # Check if any objects were detected
            for result in results[0].boxes.data.tolist():
                confidence = result[4]  # Confidence score
                class_id = int(result[5])
                if confidence > max_confidence:
                    max_confidence = confidence
                    predicted_class = model.names[class_id]

            if max_confidence >= CONFIDENCE_THRESHOLD:
                is_coffee_bean = True

        if is_coffee_bean:
            st.success("Done!")
            st.write(f"This is a {predicted_class} coffee bean.")

            # Process the detection results
            for result in results[0].boxes.data.tolist():
                class_name = model.names[int(result[5])]
                confidence = result[4]  # Confidence score
                x1, y1, x2, y2 = int(result[0]), int(result[1]), int(result[2]), int(result[3])  # Bounding box coordinates

                # Draw bounding box and label on the image
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw bounding box
                label = f"{class_name} {confidence:.2f}"  # Label with class name and confidence score
                cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36, 255, 12), 2)  # Draw label

            st.image(image, caption='Detected Objects', width=300)  # Display the image with bounding boxes and labels


            ############ FOR PROCESSING INTO THE PDF FILE ##################
            
            # Save the images to temporary files
            input_image = Image.open(uploaded_file)
            if input_image.mode == 'RGBA':
                input_image = input_image.convert('RGB')
            input_image_tempfile = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            input_image.save(input_image_tempfile.name)

            output_image_tempfile = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            output_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))  # Convert image back to PIL format
            output_image.save(output_image_tempfile.name)
            
            
            # Create and download the PDF
            pdf_file = create_pdf(input_image_tempfile.name, output_image_tempfile.name, predicted_class, max_confidence)
            # Create two columns
            col1, col2 = st.columns([1, 10])  # Adjust the ratio as needed

            with col1:
                # Display the PDF icon
                if os.path.exists(pdf_icon_path):
                    pdf_icon = Image.open(pdf_icon_path)
                    st.image(pdf_icon, width=70)
                else:
                    st.write("PDF icon not found")

            with col2:
                #Add some vertical space
                st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
                
                # Download button
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="Download Official Prediction Results",
                        data=f,
                        file_name="prediction_result.pdf",
                        mime="application/pdf"
                    )
                
            ############ FOR PROCESSING INTO THE PDF FILE ##################
            
            
            
        else:
            st.warning("This is not a coffee bean image.")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='upload-section'>Or use the camera...</div>", unsafe_allow_html=True)

    STUN_SERVER = "stun.l.google.com:19302"
    RTC_CONFIGURATION = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:" + STUN_SERVER]}]}
    )
    
    video_transformer = VideoTransformer()  # Create VideoTransformer instance

    webrtc_ctx = webrtc_streamer(
        key="example",
        mode=WebRtcMode.SENDRECV,
        video_transformer_factory=lambda: video_transformer,
        media_stream_constraints={"video": True, "audio": False},
        rtc_configuration=RTC_CONFIGURATION,
    )

if __name__ == "__main__":
    show_predict_page()