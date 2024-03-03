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
files_path ="C:/Users/Admin/Downloads/GenAI-in-Ecommerce/files"

# for APIs input/output
def handle_prompt(text):
    example_template="""You are an E-commerce company marketing specialist. your work is to write effective push notifications for a product in the cart/wishlist of the customers.
    Remember, effective push notifications should be attention-grabbing, and personalized to the user's preferences whenever possible
    Also, make sure to include a clear call-to-action (CTA). Happy generating leads!
    Output: Single More convincing push notification that mention the sales offer or some cachy lines to grab the customer attention about the product along with attractive emojis.
    
        Review text: '''{text}'''
        
        """

    example_prompt = PromptTemplate(
        input_variables=["text"],
        template=example_template
    )
    return example_prompt

def initialize_model(temperature):
    openai_model = OpenAI(
        model_name="gpt-3.5-turbo",
        openai_api_key=OPENAI_API_KEY,
        temperature = temperature,
        )
    return openai_model

