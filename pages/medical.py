import os
import streamlit as st
import google.generativeai as genai
from PIL import Image
import re  # this is required for regular expression operation (eg: @, #, +)
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

#Step1: Fetch API key. This is another method which faster than previous methods
genai.configure(api_key=os.getenv("api_key"))
 
#step2: image configuration
generation_config = {
    "temperature":1,
    "top_p": 0.95, #image quality or image resolution
    "top_k": 0, #parameters for probabilites
    "max_output_tokens": 8192, #There is no restriction
}

#step3: Safety settings is like a disclaimers to keep ourself in safezone
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

#step4: Prompt Creation
system_prompts = [
    """
    You are a domain expert in medical image analysis. You are tasked with
    examining medical images for a renowned hospital.
    Your expertise will help in identifying or
    discovering any anomalies, diseases, conditions or
    any health issues that might be present in the image.
 
    Your key responsibilites:
    1. Detailed Analysis : Scrutinize and thoroughly examine each image,
    focusing on finding any abnormalities.
    2. Analysis Report : Document all the findings and
    clearly articulate them in a structured format.
    3. Recommendations : Basis the analysis, suggest remedies,
    tests or treatments as applicable.
    4. Treatments : If applicable, lay out detailed treatments
    which can help in faster recovery.
 
    Important Notes to remember:
    1. Scope of response : Only respond if the image pertains to
    human health issues.
    2. Clarity of image : In case the image is unclear,
    note that certain aspects are
    'Unable to be correctly determined based on the uploaded image'
    3. Disclaimer : Accompany your analysis with the disclaimer:
    "Consult with a Doctor before making any decisions."
    4. Your insights are invaluable in guiding clinical decisions.
    Please proceed with the analysis, adhering to the
    structured approach outlined above.
 
    Please provide the final response with these 4 headings :
    Detailed Analysis, Analysis Report, Recommendations and Treatment
"""
]
 
#Step 5: call the Gemini pro model now
model= genai.GenerativeModel(model_name="gemini-1.5-pro-latest",generation_config=generation_config,safety_settings=safety_settings)
#latest model name can be verified here https://ai.google.dev/gemini-api/docs/models/gemini
 
# Step 6: design streamlit
st.title("Visual Medical Details 💊🌡") #try to run the app to check if it is working
st.subheader("An App to help with medical analysis using Using")
 
file_uploaded = st.file_uploader('Upload the Image for Analysis', type=['png','jpg','jpeg'])
 
if file_uploaded:
    st.image(file_uploaded, width=200, caption='upload Image')
 
submit=st.button("Generate Analysis")
 
if submit:    #configuring the submit buttton
    image_data = file_uploaded.getvalue()
 
    image_parts = [
        {
            "mime_type" : "image/jpg",
            "data": image_data
        }
    ]
 
    prompt_parts = [
        image_parts[0],
        system_prompts[0],
    ]
 
    #step 7: configuring the response
    response = model.generate_content(prompt_parts)
    if response:
        st.title('Detailed Analysis based on the Uploaded Image')
        st.write(response.text)
 
 