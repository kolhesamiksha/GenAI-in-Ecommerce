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

def initialize_model(temperature):
    openai_model = OpenAI(
        model_name="gpt-3.5-turbo-16k",
        openai_api_key=OPENAI_API_KEY,
        temperature = temperature,
        )
    return openai_model

# for APIs input/output
def review_moderation_prompt(text):
    example_template="""Develop a content moderation system for an e-commerce platform that classifies user reviews given below into different categories and assigns severity levels for each category. The categories to consider are hate, sexual content, self-harm, and violence. The severity levels range from 0 to 6.

    Given a user review, classify it into one of the following categories: hate, sexual, self-harm, or violence. Additionally, assign a severity level from 0 to 6 for each category.

    Finally, based on the severity level assigned to each category, categorize the overall risk level as follows:
    - High Risk: if the severity level is between 5 and 6.
    - Medium Risk: if the severity level is between 4 and 5.
    - Low Risk: if the severity level is between 0 and 3.

    Your task is to develop a content moderation algorithm that accurately classifies user reviews, assigns severity levels for each category, and determines the overall risk level based on the severity levels assigned.

    Striclty follow this Desired Output: show the classified category. then provide categories along with the severity scores ranges from 0-6 and after that show it's risk category based on severity score assigned/detected.

    User reviews: {text}
    
    """

    example_prompt = PromptTemplate(
        input_variables=["text"],
        template=example_template
    )

    # suffix = """
    # User: {query}
    # AI: """

    # # now create the few shot prompt template
    # few_shot_prompt_template = FewShotPromptTemplate(
    #     examples=examples,
    #     example_prompt=example_prompt,
    #     prefix=prefix,
    #     suffix=suffix,
    #     input_variables=["query"],
    #     example_separator="\n\n"
    # )
    return example_prompt

def request_classifier_prompt(text):                            
    helper_prompt = """
        You're a customer requests classifier of an e-commerce company. your work is to classify the customer requests. \n
        The customer requests are given below. \n
        each of the 10 categories has their request description with it \n
        Description contains general requests made by the customers of the e-commerce company. \n
        Description is to help you understand the customers requests. \n

    Customer Requests categories:
        1. Product inquieries
        Description: feature specification, sizes, color or materials of the product.

        2. Order Status & Tracking
        Description: status of the orders, including tracking information, estimated delivery dates, or any updates on delays or issues.

        3. Returns and Exchanges
        Description: Customers may request to return or exchange products for various reasons, such as incorrect sizing, receiving a damaged item, or changing their mind. They may need assistance with the return process, initiating a return, or understanding the refund or exchange policies.

        4. Payment & billing
        Description: Customers may encounter problems related to payments, such as declined transactions, incorrect charges, or issues with refunds. They may need support in resolving payment-related concerns. 

        5. Account Management
        Description: Customers may require assistance with managing their accounts on the e-commerce platform. This can include updating personal information, changing passwords, or managing subscriptions or saved payment methods.

        6. Technical Support
        Description: Customers may face technical issues while navigating the e-commerce website or using specific features, such as trouble logging in, difficulties placing an order, or problems with the shopping cart. They may seek technical assistance to resolve these issues.

        7. Product Reviews & Feedback
        Description:  Customers may provide feedback or leave product reviews on the e-commerce platform. They might request guidance on how to leave a review or have inquiries about existing reviews.

        8. Shipping & delivery inquiries
        Description: Customers may have questions about shipping methods, delivery times, international shipping options, or issues with missed or delayed deliveries.

        9. Coupons, Discounts, and Promotions
        Description: Customers may inquire about available discounts, coupon codes, or promotions applicable to their purchases. They may need assistance in applying these offers during the checkout process.

        10. Customer Account Suspension or Closure
        Description: customers may request the suspension or closure of their e-commerce accounts. They may have privacy concerns, wish to unsubscribe from marketing communications, or want their personal information removed from the system.
    
    Desired Output Format: Classified category.

    Review text: {text}
    """

    example_prompt = PromptTemplate(
        input_variables=["text"],
        template=helper_prompt
    )
    return example_prompt

def brand_prompt(text):
    example_template = """Generate unique and trademarked brand name ideas for a {text} company.
        Brand names are memorable, easy and pleasant to pronounce, aligned with the company’s image, self-explanatory and should also represent the essence of the product.
        Brand names should align with the company description and adhere to trademark availability.

        Follow the guidelines below to generate the best brand names:
            1. Ensure the name is memorable, easy to spell, and pronounce.
            2. Align the name with your industry and target audience.
            3. Avoid using numbers, hyphens, or complicated words.
            4. Consider how the name translates into a visually appealing logo or brand image.
            5. Check trademark availability to ensure legal protection.
            6. Choose a brand name that has the potential to scale and grow.
            7. Limited to one word only
            8. Avoid generic words
            9. No negative aonnotations should be present
            10. Not imitating existing brand names to avoid copywriting problem.
    
        Below are some brand names and their Brand_naming intuition, that you can consider for adding uniqueness & creativity while generating the brand name.

        Brand_name: ZOMATO
        Brand_name_intuition: the word ZOMATO got inspired from the word TOMATO because it is the part of most of the foods and adds a lot of flavours into it. As a matter of fact, the actual name of Zomato is Foodiebay which is not so easy to speak as well as a little bit boring.
        Brand_name: Nike
        Brand_name_intuition: NIKE, Inc., named for the Greek goddess of victory, is the world's leading designer, marketer, and distributor of authentic athletic footwear, apparel, equipment, and accessories for a wide variety of sports and fitness activities
        Brand_name: OLA
        Brand_name_intuition: Hola !! ( spanish) H is silent so ola ..a general word to greet people around in Spain ,typically hello in English .Founders some how connected to this . Just observe all the messages start with ola driver has arrived .. hello . Your driver arrived
        
        Args:
            {text}: The company description or relevant brand information.

        Returns:
        CSV format with columns mentioned below and 5 rows with the brand_names. Provide Top 5 distinctive, attractive, and trademarked brand name.
        1.brand_name: 
        2.Slogan: cachy slogan about the brand to attract the customers
        3.Rating: star rating out of 5 to each generated brand name based on the most best similarty score with provided context.
        """

    example_prompt = PromptTemplate(
        input_variables=["text"],
        template=example_template
      )

    return example_prompt

def product_prompt(text):
    example_template = """Generate unique and catchy product names for a {text}.

        Product names should be memorable, easy to spell and pronounce, aligned with the product's purpose, and appealing to the target audience. They should also be distinctive and have the potential to create a strong brand identity.

        Follow the guidelines below to generate the best product names:
            1. Ensure the name is easy to remember and pronounce.
            2. Align the name with the product's purpose and target audience.
            3. Avoid using numbers, hyphens, or complicated words.
            4. Consider how the name translates into a visually appealing logo or product packaging.
            5. Choose a product name that has the potential to stand out in the market.
            6. Limited to one or two words only.
            7. Avoid generic words.
            8. No negative connotations should be present.
            9. Not imitating existing product names to avoid trademark issues.

        Below are some examples of product names and their intuitive explanations that you can consider for adding uniqueness and creativity while generating the product names:

        Product_name: Fitbit
        Product_name_intuition: The word "fit" represents physical fitness, and the "bit" emphasizes the small, wearable nature of the product, which tracks fitness-related data.

        Product_name: TikTok
        Product_name_intuition: The word "tik" represents the short duration of the videos shared on the platform, while "tok" mimics the sound of a clock ticking, emphasizing the fast-paced and time-bound nature of the content.

        Product_name: Kindle
        Product_name_intuition: The word "kindle" refers to igniting or sparking an interest, reflecting the purpose of the e-reader to ignite a love for reading.

        Args:
            {text}: The product description or relevant information about the product.

        Returns:
            list: A list of up to 5 unique, catchy, and distinctive product names that align with the product's purpose and target audience. Please provide a brief intuitive explanation for each product name ot convince regards choosing that particular product_name.
    
    """

    example_prompt = PromptTemplate(
        input_variables=["text"],
        template=example_template
    )
    return example_prompt

def product_review_summarisation(text):
    helper_prompt = """ You are an E-commerce Product reviews summariser. You understand the e-commerce business and understands the customer reviews from their reviews.
    You have to Summarise the Review text of Product reviews. 
    The review is delimited with triple backticks.
    follow below stratergy to effectively summarise the e-commerce product reviewws:
    1. Extract the products from the review.
    2. based on the product extract very specific information that will help to summarise more specific and up to point for customer aspect analysis.
 
    Summarised output should be 3-4 lines long only.
        Review text: '''{text}'''

    """

    example_prompt = PromptTemplate(
        input_variables=["text"],
        template=helper_prompt,
    )
    return example_prompt

def review_sentiment_prompt(text):        
    helper_prompt = """
              Identify the following items from the review text: 
            - Sentiment (positive or negative or neutral)
            - Is the reviewer expressing anger? (true or false)
            - Item purchased by reviewer
            - Company that made the item

        The review is delimited with triple backticks. \
        Format your response as a JSON object with \
        "Sentiment", "Anger", "Item" and "Brand" as the keys.
        If the information isn't present, use "unknown" \
        as the value.
        Make your response as short as possible.
        Format the Anger value as a boolean.

        Review text: '''{text}'''

    """

    example_prompt = PromptTemplate(
        input_variables=["text"],
        template=helper_prompt,
    )
    return example_prompt

# for APIs input/output
def negotiate_seller_prompt(history, input):
    template = """You are an E-commerce chatbot acting as an Account Manager, who talks with seller, negotiate regarding the price of the product, convice the seller at par to lower down it's price by any means possible. and end the conversation.

        {history}
        Seller: {input}
        Account_Manager:"""

    prompt = PromptTemplate(
        input_variables=["history", "input"], template=template
    )

    return prompt