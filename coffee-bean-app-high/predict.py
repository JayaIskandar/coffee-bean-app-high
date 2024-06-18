import os
import streamlit as st
from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
from user_agents import parse
from streamlit_javascript import st_javascript

# Set the working directory to the script's directory
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, 'best.pt')
css_path = os.path.join(base_dir, 'style.css')
html_path = os.path.join(base_dir, 'predict.html')

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
    img = resize_with_padding(img, 300, 300, (128, 128, 128), scale_factor=0.25)  # Resize and pad the image to 300x300 with gray background
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
        self.model = YOLO(model_path)

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        results = detect_objects(img)
        if results[0].boxes.data.tolist():  # Check if any objects were detected
            for result in results[0].boxes.data.tolist():
                class_name = self.model.names[int(result[5])]
                confidence = result[4]  # Confidence score
                x1, y1, x2, y2 = int(result[0]), int(result[1]), int(result[2]), int(result[3])  # Bounding box coordinates

                # Draw bounding box and label on the image
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw bounding box
                label = f"{class_name} {confidence:.2f}"  # Label with class name and confidence score
                cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36, 255, 12), 2)  # Draw label

        return img

def is_mobile(user_agent):
    parsed_user_agent = parse(user_agent)
    return parsed_user_agent.is_mobile or parsed_user_agent.is_tablet

def show_predict_page():
    st.markdown("<div class='upload-section'>Upload an image or use the webcam...</div>", unsafe_allow_html=True)

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
        else:
            st.warning("This is not a coffee bean image.")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='upload-section'>Or use the webcam...</div>", unsafe_allow_html=True)

    user_agent = st_javascript("return navigator.userAgent;")

    if user_agent:
        if is_mobile(user_agent):
            webrtc_ctx = webrtc_streamer(
                key="example", 
                mode=WebRtcMode.SENDRECV, 
                video_transformer_factory=VideoTransformer, 
                media_stream_constraints={"video": True, "audio": False}
            )
        else:
            st.write("Camera is only available to be used on a phone.")

if __name__ == "__main__":
    show_predict_page()
