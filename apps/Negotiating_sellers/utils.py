from langchain import FewShotPromptTemplate
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

import os
import streamlit as st
from PIL import Image
from io import BytesIO
import base64

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# for APIs input/output
def handle_prompt(history, input):
    template = """You are an E-commerce chatbot acting as an Account Manager, who talks with seller, negotiate regarding the price of the product, convice the seller at par to lower down it's price by any means possible. and end the conversation.

        {history}
        Seller: {input}
        Account_Manager:"""

    prompt = PromptTemplate(
        input_variables=["history", "input"], template=template
    )

    return prompt

def initialize_model(temperature):
    openai_model = OpenAI(
        model_name="gpt-3.5-turbo-16k",
        openai_api_key=OPENAI_API_KEY,
        temperature = temperature,
        )
    return openai_model

