import streamlit as st
from langchain.chat_models import ChatOpenAI
from streamlit_option_menu import option_menu
import hydralit_components as hc
import pickle
import os
import pandas as pd

from utils import (
    brand_prompt,
    product_prompt,
    request_classifier_prompt,
    review_moderation_prompt,
    review_sentiment_prompt,
    product_review_summarisation,
    initialize_model,
    save_files,
    Web_Loader,
    File_Loader
)

from text_to_image import (
    generate
)

import random
import string
import chardet
import json

# langchain modules
from langchain import FewShotPromptTemplate
from langchain import PromptTemplate

import requests
from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title='Content_Moderation', 
    page_icon = im, 
    initial_sidebar_state = 'auto'
)

menu_data = [
        {'icon':"🔃",'label':"Brandify"},
        {'icon':"🔃",'label':"Customer Request Classification"},
        {'icon':"🔃",'label':"Product Reviews Summarisation_and_intent_identification"},
        {'icon':"🔃",'label':"Product Review Moderation"}
]

over_theme = {'txc_inactive': '#ffffff','menu_background':'#5c31ff'}
menu_id = hc.nav_bar(menu_definition=menu_data,home_name='About',override_theme=over_theme)

openai_model = initialize_model(0.6)

files_path ="C:/Users/Admin/Downloads/GenAI-in-Ecommerce/apps/files"

if menu_id=="Brandify":
    with st.sidebar:
        selected = option_menu(
            menu_title = "Main Menu",
            options = ["About the App","Inference", "Batch Inference"])

    if selected=="About the App":
        with open("doc/brandify.md","r") as f:
            content = f.read() 
        st.write(content)
    
    def text_input(prompt_template,input_text):
        prompt_template = prompt_template(input_text)
        prompt_output = prompt_template.format(text=input_text)
        brand_name = openai_model(prompt_output)
        return brand_name

    #for File as input
    def file_uploader(path_list,input_prompt):
        batch_csv = pd.DataFrame()
        batch_json = {}
        file_uploaded = save_files(path_list)
        if file_uploaded:
            files_list = os.listdir(path_list)
            print(files_list)
            data_list = File_Loader(files_list)
            # concatinating same file data
            data_list_concat = []
            data_list_source = []
            text = ""
            previous_name = ""
            previous_page = -1
            for data in data_list:
                name = data.metadata["source"]
                #page = data.metadata["page"]
                if previous_name == name:# and previous_page != page:
                    text += data.page_content
                    previous_name = data.metadata["source"]
                    #previous_page = data.metadata["page"]
                else:
                    if len(text) > 0:
                        data_list_concat.append(text)
                        data_list_source.append(previous_name)
                    previous_name = data.metadata["source"]
                    # previous_page = data.metadata["page"]
                    text = data.page_content
            data_list_concat.append(text)
            data_list_source.append(previous_name)

            for index, (data, source) in enumerate(zip(data_list_concat, data_list_source)):
                query = data
                prompt_template = input_prompt(query)
                result = llm_model(prompt_template.format(query=query))
                batch_json[source] = result
                batch_csv.loc[index, "source"] = source.split("/")[-1]
                batch_csv.loc[index, "Output"] = result

            #convert to csv format
            batch_csv= batch_csv.to_csv(index=False)

            #convert to json format
            batch_json= json.dumps(batch_json)

        return batch_csv,batch_json

    select_option = st.sidebar.selectbox("choose your naming purpose",("Brand_Name","Product_Name"))
    if selected=="Inference":
        input_option = st.radio("Choose the input",("Text","Link"))
        form, param = st.columns([10,1.5])
        with st.expander("Text-to-image parameters"):
            with param:
                negative_prompt = st.text_input("write any negative prompt")
                num_inference_steps = st.slider(label="Inference Steps", min_value=1, max_value=100, value=25,
                                    help="In how many steps will the denoiser denoise the image?")

                guidance =  st.slider(label="Guidance Scale", min_value=1, max_value=20, value=7, 
                                    help="Controls how much the text prompt influences the result")
                img_width = st.slider(label="Image Width", min_value=64, max_value=512, step=64, value=512)
                img_height = st.slider(label="Image Height", min_value=64, max_value=512, step=64, value=512)

        #for text as input
        with form:
            if select_option=="Brand_Name":
                st.subheader("Name your Brand and Advertise")
                if input_option == "Text":
                    input_text = st.text_area("Enter the input description",height=400)
                    if st.button("Generate Brand Advert"):
                        with st.spinner("Processing... This may take a while⏳"):
                            st.subheader("Brand Name Suggestions:")
                            col1,col2 = st.columns(2)
                            with col1: 
                                brand_desc = st.text_area("Suggested Brand Names",value = text_input(brand_prompt,input_text),height=400)
                                print(f"dtype of brand description : {type(brand_desc)}, brand_desc: {brand_desc[0]}")
                            with col2:
                                output = generate(brand_desc,negative_prompt,num_inference_steps,guidance,img_width,img_height)
                                output = output.resize((600,600))
                                st.image(output)          

                                # image = Image.open(output)

                                # # Convert the image to binary data
                                # buffer = io.BytesIO()
                                # image.save(buffer, format="JPEG")
                                # image_binary = buffer.getvalue()

                                # # Create a download button with the binary data
                                # st.download_button(label="Download Image", data=image_binary, file_name="image.jpg")
                    else:
                        st.warning("Please enter a company description.")
            
            # weblink of the company or products
            # if input_option == "Link":
            #     web_link = st.text_input("Enter the web link")
            #     ifst.button("Generate Brand Advert"):
            #         with st.spinner("Processing... This may take a while⏳"):
            #             st.text_area("Suggested Brand Names",value = link_input(brand_prompt,web_link),height=400)
                    
            # for text as input
            if select_option=="Product_Name":
                st.subheader("Name your Product and Advertise")
                if input_option == "Text":
                    input_text = st.text_area("Enter the input description")
                    if st.button("Generate Product Advert"):
                        with st.spinner("Processing... This may take a while⏳"):
                            st.text_area("Suggested Product Names",value = text_input(product_prompt,input_text),height=400)
                    else:
                        st.warning("Please enter a product description.")
        
            # if input_option == "Link":
            #     web_link = st.text_input("Enter the web link")
            #     if st.button("Generate Product Advert"):
            #         with st.spinner("Processing... This may take a while⏳"):
            #             input_prompt = product_prompt()
            #             st.text_area("Suggested Product Names",value = link_input(product_prompt,web_link),height=400)

    if selected=="Batch Inference":
        if select_option=="Brand_Name":
            st.subheader("Name your Brand or Product")
            #upload any company significant doc
            uploaded_file = st.file_uploader("Upload file for inference", accept_multiple_files=True, type=["csv", "pdf", "txt", "docx"])
            if uploaded_file is not None:
                if st.button("Generate Brand Advert"):
                        with st.spinner("Processing... This may take a while⏳"):
                            csv_file,json_file = file_uploader(uploaded_file,brand_prompt)

                            #download csv result
                            st.download_button(label='📥 Download Result in csv',
                                                    data=csv_file,
                                                    file_name= 'Result.csv')
                
                            #download the json result
                            st.download_button(label='📥 Download Result in json',
                                                    data=json_file,
                                                    mime="application/json",
                                                    file_name= 'Result.json')

        if select_option=="Product_Name":

            #upload any company significant doc
            uploaded_file = st.file_uploader("Upload file for inference", accept_multiple_files=True, type=["csv", "pdf", "txt", "docx"])
            if uploaded_file is not None:
                if st.button("Generate Product Advert"):
                        with st.spinner("Processing... This may take a while⏳"):
                            csv_file,json_file = file_uploader(uploaded_file,product_prompt)

                            #download the csv result
                            st.download_button(label='📥 Download Result in csv',
                                                    data=csv_file,
                                                    file_name= 'Result.csv')
                
                            #download the json result
                            st.download_button(label='📥 Download Result in json',
                                                    data=json_file,
                                                    mime="application/json",
                                                    file_name= 'Result.json')

if menu_id=="Customer Request Classification":
    with st.sidebar:
        selected = option_menu(
            menu_title = "Main Menu",
            options = ["About the App","Inference", "Batch Inference"])

    if selected=="About the App":
        with open("doc/customer_request_classification.md","r") as f:
            content = f.read() 
        st.write(content)
    
    if selected == "Inference":
        st.subheader("Customer Request Classification")
        col1, col2 = st.columns(2)
        with col1:
            user_input = st.text_area("Query *",height=400)
            submitt = st.button("Classify Request")
        
        with col2:
            if submitt:
                with st.spinner("This may take a moment..."):
                    prompt_template = request_classifier_prompt(user_input)
                    prompt_text = prompt_template.template.format(text=user_input)
                    model_reply = openai_model(prompt_text)
                    print("Model Reply:", model_reply)
                    st.text_area("Classified Request",value=model_reply,height=400)                       # Print the model's reply for debugging purposes

    if selected == "Batch Inference":
        st.subheader("Customer Request Classification")
        uploaded_file = st.file_uploader("Upload file for inference", accept_multiple_files=True, type=["csv", "pdf", "txt", "docx"])
        if uploaded_file is not None:
            if st.button("Classify request"):
                    with st.spinner("Processing... This may take a while⏳"):
                        csv_file,json_file = file_uploader(uploaded_file,product_prompt)

                        #download the csv result
                        st.download_button(label='📥 Download Result in csv',
                                                data=csv_file,
                                                file_name= 'Result.csv')
            
                        #download the json result
                        st.download_button(label='📥 Download Result in json',
                                                data=json_file,
                                                mime="application/json",
                                                file_name= 'Result.json')

if menu_id=="Product Reviews Summarisation_and_intent_identification":
    with st.sidebar:
        selected = option_menu(
            menu_title = "Main Menu",
            options = ["About the App","Inference", "Batch Inference"])

    if selected=="About the App":
        with open("doc/product_review_sentiment_analysis.md","r") as f:
            content = f.read() 
        st.write(content)
    
    if selected == "Inference":
        st.subheader("Product Reviews Sentiment analysis")
        

        user_input = st.text_area("Query *",height=400) 
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Summarise Review"):
                with st.spinner("This may take a moment..."):
                    prompt_template = product_review_summarisation(user_input)
                    prompt_text = prompt_template.template.format(text=user_input)
                    model_reply = openai_model(prompt_text)
                    print("Model Reply:", model_reply)
                    st.text_area("Summarise Reviews",value=model_reply,height=400)                       # Print the model's reply for debugging purposes
        
        with col2:
            if st.button("Analyse Sentiment"):
                with st.spinner("This may take a moment..."):
                    prompt_template = review_sentiment_prompt(user_input)
                    prompt_text = prompt_template.template.format(text=user_input)
                    model_reply = openai_model(prompt_text)
                    print("Model Reply:", model_reply)
                    st.text_area("Classified Sentiment",value=model_reply,height=400) 

    if selected == "Batch Inference":
        st.subheader("Product Reviews Sentiment analysis")
        uploaded_file = st.file_uploader("Upload file for inference", accept_multiple_files=True, type=["csv", "pdf", "txt", "docx"])
        if uploaded_file is not None:
            if st.button("Analyse Sentiment"):
                with st.spinner("Processing... This may take a while⏳"):
                    csv_file,json_file = file_uploader(uploaded_file,product_prompt)

                    #download the csv result
                    st.download_button(label='📥 Download Result in csv',
                                            data=csv_file,
                                            file_name= 'Result.csv')
        
                    #download the json result
                    st.download_button(label='📥 Download Result in json',
                                            data=json_file,
                                            mime="application/json",
                                            file_name= 'Result.json')

if menu_id=="Product Review Moderation":
    with st.sidebar:
        selected = option_menu(
            menu_title = "Main Menu",
            options = ["About the App","Inference", "Batch Inference"])

    if selected=="About the App":
        with open("doc/product_review_moderation.md","r") as f:
            content = f.read() 
        st.write(content)

    if selected == "Inference":
        st.subheader("Product Review Moderation")
        user_input = st.text_area("Query *",height=400)
        submitt = st.button("Moderate reviews")
        
        if submitt:
            with st.spinner("This may take a moment..."):
                prompt_template = review_moderation_prompt(user_input)
                prompt_text = prompt_template.template.format(text=user_input)
                model_reply = openai_model(prompt_text)
                print("Model Reply:", model_reply)
                st.text_area("Review_Moderation",value=model_reply,height=400)                       # Print the model's reply for debugging purposes

    if selected == "Batch Inference":
        st.subheader("Moderation for Content Safety")
        uploaded_file = st.file_uploader("Upload file for inference", accept_multiple_files=True, type=["csv", "pdf", "txt", "docx"])
        if uploaded_file is not None:
            if st.button("Moderate review"):
                with st.spinner("Processing... This may take a while⏳"):
                    csv_file,json_file = file_uploader(uploaded_file,product_prompt)

                    #download the csv result
                    st.download_button(label='📥 Download Result in csv',
                                            data=csv_file,
                                            file_name= 'Result.csv')
        
                    #download the json result
                    st.download_button(label='📥 Download Result in json',
                                            data=json_file,
                                            mime="application/json",
                                            file_name= 'Result.json')
    
