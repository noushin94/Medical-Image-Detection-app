# Import necessary modules
import streamlit as st
from pathlib import Path
import re
import google.generativeai as genai

# Replace with your valid API key
api_key = "AIzaSyBBdPj-8zPxtlmgCywKmBRH6I8G4W8NjMA"
# Configure the genai with the API key
genai.configure(api_key=api_key)

# System prompt for the model
system_prompt = """Hello, I have uploaded a medical image and need your assistance in identifying it. Please analyze the image and provide the following information:

Identify the type of medical imaging used (e.g., X-ray, MRI, CT scan).
Describe the visible anatomical structures (e.g., bones, organs).
Highlight any abnormalities or notable features (e.g., fractures, lesions).
Suggest possible medical conditions that might be indicated by the features observed in the image.
Recommend further tests or examinations that might be necessary based on the image analysis.
Please base your analysis on the image provided and use your trained knowledge to deliver the most accurate assessment. Thank you!"""

# Set up model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Set the page configuration
st.set_page_config(page_title="Medical Image Analytics", page_icon=":robot:")

# Set the logo
st.image("logo.png", width=200)

# Set the title
st.markdown('<h1 style="color: gray;">🔬 Medical Image Analytics</h1>', unsafe_allow_html=True)

# Import Google Font
font_url = "https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@400&display=swap"
st.markdown(f'<link href="{font_url}" rel="stylesheet">', unsafe_allow_html=True)

# Set a custom-styled subheader
st.markdown('<h2 style="font-family:Roboto Condensed; color: slategray;">An application that can help individuals to identify medical images</h2>', unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Please upload your medical image to be identified", type=["png", "jpg", "jpeg"])

# Start analysis button
submit_button = st.button("Start Analysis")

if submit_button:
    if uploaded_file is not None:
        # Retrieve image data from a file-like object
        image_data = uploaded_file.getvalue()
        
        # Generate a valid file name
        def generate_valid_file_name(filename):
            # Replace non-alphanumeric characters with dashes and convert to lowercase
            valid_filename = re.sub(r'[^a-z0-9]+', '-', filename.lower()).strip('-')
            return valid_filename
        
        original_filename = uploaded_file.name
        valid_filename = generate_valid_file_name(original_filename)
        image_path = Path(valid_filename)

        # Write image data to a file
        with open(image_path, "wb") as f:
            f.write(image_data)

        # Function to upload content to Gemini
        def upload_to_gemini(file_path):
            """Uploads the given file to Gemini."""
            try:
                file = genai.upload_file(str(file_path), name=file_path.name)
                st.success(f"Uploaded file '{file.display_name}' as: {file.uri}")
                return file
            except Exception as e:
                st.error(f"Failed to upload the file: {e}")
                return None

        # Upload the file and receive a reference to the uploaded file
        uploaded_image = upload_to_gemini(image_path)

        if uploaded_image:
            try:
                # Start a chat session with the model
                chat_session = model.start_chat()  # Check your API on how to correctly start a session

                # Send the uploaded image's URI in a message
                response = chat_session.send_message(f"Please analyze this image: {uploaded_image.uri}")

                # Print the model's response
                st.write(response.text)
            except Exception as e:
                st.error(f"Failed to process the image: {e}")
        else:
            st.error("File upload failed, cannot proceed with analysis.")
    else:
        st.error("Please upload a file before pressing 'Start Analysis'.")
