import streamlit as st
from langchain import FewShotPromptTemplate
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from streamlit_option_menu import option_menu
import pickle
import os
import pandas as pd
from utils import handle_prompt, initialize_model

import random
import string
import chardet
import json

import requests
from PIL import Image
from io import BytesIO

from utils import (
    handle_prompt,
    initialize_model,
)

from text_to_image import (
    generate
)

openai_model = initialize_model(0.6)
files_path ="C:/Users/Admin/Downloads/GenAI-in-Ecommerce/files"

st.set_page_config(
    page_title="push_notifications", 
    layout = 'wide', 
    initial_sidebar_state = 'auto'
)


with st.sidebar:
        selected = option_menu(
            menu_title = "Main Menu",
            options = ["About the App","Inference"])
        
if selected=="About the App":
    with open("doc/readme.md","r") as f:
        content = f.read() 
    st.write(content)

if selected=="Inference":
    form, param = st.columns([4,1.5])
    with st.expander("Text-to-image parameters"):
        with param:
            negative_prompt = st.text_input("write any negative prompt")
            num_inference_steps = st.slider(label="Inference Steps", min_value=1, max_value=100, value=25,
                                help="In how many steps will the denoiser denoise the image?")

            guidance =  st.slider(label="Guidance Scale", min_value=1, max_value=20, value=7, 
                                help="Controls how much the text prompt influences the result")
            img_width = st.slider(label="Image Width", min_value=64, max_value=768, step=64, value=512)
            img_height = st.slider(label="Image Height", min_value=64, max_value=768, step=64, value=512)
    
        with form:
                st.subheader("Push Notification Generator")
                input_text = st.text_area("Enter the product desription",height=50)
                if st.button("generate push notification"):
                    with st.spinner("Processing... This may take a while⏳"):
                        output = generate(input_text,negative_prompt,num_inference_steps,guidance,img_width,img_height)
                        st.image(output)
                        prompt_template = handle_prompt(input_text)
                        prompt_text = prompt_template.template.format(text=input_text)
                        model_reply = openai_model(prompt_text)
                        st.text_area("Convincing Text",value =model_reply ,height=400)
                        
                else:
                    st.warning("Please enter a product name")
        