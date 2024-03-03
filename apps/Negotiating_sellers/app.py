import streamlit as st
from langchain import FewShotPromptTemplate
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from streamlit_option_menu import option_menu
import pickle
import os
import pandas as pd
from langchain.chains import ConversationChain
#from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI
from utils import handle_prompt, initialize_model

import random
import string
import chardet
import json

import requests
from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title='Negotiate_sellers', 
    layout = 'wide', 
    initial_sidebar_state = 'auto'
)

with st.sidebar:
        selected = option_menu(
            menu_title = "Main Menu",
            options = ["About the App","Inference"])

if selected =="About the App":
    with open("doc/readme.md","r") as f:
        content = f.read()
    st.write(content)

# if selected == "Extraction":
#     st.write("Extraction")

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

if selected=="Inference":

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
   
    st.title("Negotiate with seller")

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

    prompts_template = handle_prompt(history=st.session_state.past, input=st.session_state.input)

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
        
