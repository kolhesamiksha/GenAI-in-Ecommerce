import streamlit as st
import pandas as pd
import numpy as np 
from streamlit_option_menu import option_menu
import pickle
import os

# import langchain requirements
from langchain import FewShotPromptTemplate
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.llms import OpenAI
#from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE


# #import app modules
from utils.prompt_templates import (
    initialize_model,
    negotiate_seller_prompt,
    request_classifier_prompt,
    product_review_summarisation,
    review_moderation_prompt,
    brand_prompt,
    product_prompt,
    save_files,
    Web_Loader,
    File_Loader
)
from utils.text_to_image import (
    generate
)

st.set_page_config(
    page_title='Content_Moderation',  
    initial_sidebar_state = 'auto'
)

openai_model = initialize_model(0.6)

files_path ="C:/Users/Admin/Downloads/GenAI-in-Ecommerce/files"

text_style = "color: #000000; font-size: 30px; background-color: #ffc0cb; padding: 10px; display: inline-block; width: 100%; font-weight: bold;"
st.sidebar.markdown(f'<p style="{text_style}">NexGenShop</p>', unsafe_allow_html=True)

with st.sidebar:
    menu_id = option_menu("Main Menu", ["Personalized RecommendationSys","Outfit Generator", "Brandify", 'Customer Request Classification','Product Reviews Summarisation & intent identification','Product Review Moderation','Negotiating Sellers'])

if menu_id=="Personalized RecommendationSys":
    st.title("Personalised Recommendation")

if menu_id=="Outfit Generator":
    st.title("Outfit Generator")

if menu_id=="Brandify":
    st.title("Your Branding App")
    options = ['None','text', 'file']

    selected = st.selectbox("select type of input", options)

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
            print("Path List", path_list)
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
    if selected=="text":
        form, param = st.columns([7,2])
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
                    
            # for text as input
            if select_option=="Product_Name":
                st.subheader("Name your Product and Advertise")
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

    if selected=="file":
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
    st.title("Customer Request Classification")
    
    options = ['None','text', 'file']

    selected = st.selectbox("select type of input", options)
    
    if selected == "text":
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

    if selected == "file":
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

if menu_id=="Product Reviews Summarisation & intent identification":
    st.title("Product Reviews Summarisation & intent identification")
    
    options = ['None','text', 'file']

    selected = st.selectbox("select type of input", options)
    
    if selected == "text":
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

    if selected == "file":
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
    st.title("Product Review Moderation")
    
    options = ['None','text', 'file']

    selected = st.selectbox("select type of input", options)

    if selected == "text":
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

    if selected == "file":
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
    
if menu_id=="Negotiating Sellers":
    st.title("Negotiate with seller")

    def new_chat():
        """
        Clears session state and starts a new chat.
        """
        save = []
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            save.append("Seller:" + st.session_state["past"][i])
            save.append("Account_Manager:" + st.session_state["generated"][i])        
        st.session_state["stored_session"].append(save)
        st.session_state["generated"] = []
        st.session_state["past"] = []
        st.session_state["input"] = ""
        st.session_state.entity_memory.store = {}
        st.session_state.entity_memory.buffer.clear()

    def clear_text():
        st.session_state["temp"] = st.session_state["input"]
        st.session_state["input"] = ""

    def get_text():
        """
        Get the user input text.

        Returns:
            (str): The text entered by the user
        """
        input_text = st.text_input("Seller: ", st.session_state["input"], key="input", 
                                placeholder="You're a seller! Negotiate with your product value.", 
                                on_change=clear_text,    
                                label_visibility='hidden')

        input_text = st.session_state["temp"]
        return input_text

    llm = initialize_model(0.7)


    if "generated" not in st.session_state:
        st.session_state["generated"] = []
    if "past" not in st.session_state:
        st.session_state["past"] = []
    if "input" not in st.session_state:
        st.session_state["input"] = ""
    if "stored_session" not in st.session_state:
        st.session_state["stored_session"] = []
    if "just_sent" not in st.session_state:
        st.session_state["just_sent"] = False
    if "temp" not in st.session_state:
        st.session_state["temp"] = ""

    K = 10

    hide_default_format = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        """
    
    st.markdown(hide_default_format, unsafe_allow_html=True)

    # Create a ConversationEntityMemory object if not already created
    if 'entity_memory' not in st.session_state:
            st.session_state.entity_memory = ConversationBufferWindowMemory(k=K)

    user_input = get_text() 

    prompts_template = negotiate_seller_prompt(history=st.session_state.past, input=st.session_state.input)

    # Create the ConversationChain object with the specified configuration
    Conversation = ConversationChain(
            llm=llm, 
            prompt=prompts_template,
            memory=st.session_state.entity_memory
        ) 

    # Generate the output using the ConversationChain object and the user input, and add the input/output to the session
    if user_input:
        output = Conversation.run(input=user_input)  
        st.session_state.past.append(user_input)  
        st.session_state.generated.append(output)  

    download_str = []
    
    with st.expander("Conversation", expanded=True):
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            st.info(st.session_state["past"][i],icon="🧐")
            st.success(st.session_state["generated"][i], icon="🤖")
            download_str.append(st.session_state["past"][i])
            download_str.append(st.session_state["generated"][i])
                                
        download_str = '\n'.join(download_str)
    #    word_count += count_words(download_str)
        
        if download_str:
            st.download_button('Download',download_str)

    # Display stored conversation sessions in the sidebar
    for i, sublist in enumerate(st.session_state.stored_session):
            with st.sidebar.expander(label= f"Conversation-Session:{i}"):
                st.write(sublist)

    # Allow the user to clear all stored conversation sessions
    if st.session_state.stored_session:   
        if st.sidebar.checkbox("Clear-all"):
            del st.session_state.stored_session
