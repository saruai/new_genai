import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import pandas as pd
import re   #this is regular expression(#,$,@)
from pdf2image import convert_from_bytes    #this has to be installed

# Step 1: Load API Key from .env
load_dotenv()
google_api_key = os.getenv("api_key")
 
# Step 2: Configure GenAI
genai.configure(api_key=google_api_key)
 
# Step 3: Load Gemini Pro Model
model=genai.GenerativeModel('gemini-pro')

# Step 4: Create "images" folder   # configure image folder here
output_path = "images"
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Step 5: Define function to convert PDF to images
def pdf_to_images(pdf_file, output_path):
    images = convert_from_bytes(pdf_file.read())
    for i, image in enumerate(images): #enumerate means it will convert into images
        image_path = os.path.join(output_path, f'page_{i+1}.jpg')
        image.save(image_path, 'JPEG')

# Step 6: Load Gemini Vision Model & configure the response
def gemini_vision_response(input_text, image):
    vmodel = genai.GenerativeModel('gemini-pro-vision')
    try:
        response = vmodel.generate_content([input_text, image])
        if response.result:
            return response.result.candidates[0].content.parts[0].text
        else:
            return "No result found"
    except TimeoutError as e:
        return f"Timeout error: {e}"
    except Exception as e:
        return f"An error occurred: {e}"
    
# Step 7: Extract company details
def extract_company_details(response):
    pattern = r".+?,.+?,.+?,.+"
    matches = re.findall(pattern, response)
    # Split each match into a list of four elements
    matches = [match.split(",") for match in matches]
    # Filter rows with null values and rows with more than 4 columns
    matches = [
        match for match in matches
        if not any(field.strip().lower() == 'na' for field in match) and len(match) == 4
    ]
    return matches

# Step 8: Define custom prompt
custom_inst = '''Extract company details including company name, email addresses, phone numbers, and website links in comma-separated format.
Ensure accuracy and refrain from including additional information beyond the CSV format.
Desired output format:
Company Name, Email address, phone number, website
For example:
Apple Inc., info@apple.com, +1-(800)-555-9876, www.apple.com
Google, info@google.com, +91-1234567890, www.google.com
Please provide only the necessary details as mentioned above. Do not include any additional information such as page number or any other extraneous content.
'''

# Step 9: Frontend page design
st.title("Company Details Extractor")
 
pdf_files = st.file_uploader("Choose multiple files...", type="pdf", accept_multiple_files=True)

# Step 10: Configure the output
response = []
 
if pdf_files:
    for pdf_file in pdf_files:
        pdf_to_images(pdf_file, output_path)
        image_folder = "images"
 
        if os.path.exists(image_folder):
            st.write(f"Processing Images from PDF: {pdf_file.name}")
            for filename in os.listdir(image_folder):
                if filename.lower().endswith((".jpg", '.jpeg', '.png')):
                    st.write(f"Processing Image: {filename}")
                    image_path = os.path.join(image_folder, filename)
                    image = Image.open(image_path)
                    input_text = custom_inst
                    img_response = gemini_vision_response(input_text, image)
                    response.extend(extract_company_details(img_response))
 
        if response:
            df = pd.DataFrame(response, columns=["Company Name", "Email address", "phone number", "website"])
            st.write(df)
 
            # Step 11: Saving dataframe to CSV file
            csv_file_path = "gemini_response.csv"
            df.to_csv(csv_file_path, index=False)
            st.write(f"Response is saved to CSV file: {csv_file_path}")
        else:
            st.write("No response to save.")
 
# Step 12: Delete all processed images
def delete_images(output_path):
    for filename in os.listdir(output_path):
        file_path = os.path.join(output_path, filename)
        if os.path.isfile(file_path) and filename.lower().endswith('.jpg'):
            os.remove(file_path)
 
delete_images(output_path)
 