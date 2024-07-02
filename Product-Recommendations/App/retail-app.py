#streamlit dependencies
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components

# general dependencies
import os
import requests
import pandas as pd
from PIL import Image
from io import BytesIO
from base64 import b64encode
import base64

from utils import product_vector_search, personal_vector_search

routes = os.environ["ROUTE"]

st.set_page_config(
    page_title="retail-recommendation", 
    page_icon = im, 
    layout = 'wide', 
    initial_sidebar_state = 'auto'
)

if "selected_user" not in st.session_state:
    st.session_state.selected_user = ""
    st.session_state.query = ""

url_params = st.experimental_get_query_params()
selected_option = url_params.get("selected_option", "")
query_param = url_params.get("query", "")
st.session_state.query = query_param

def display_images_horizontal(image_urls, brands, prices, ratings, categories, rec_type):
    desired_width = 190 
    desired_height = 200  
 
    # Create an expander for the image grid
    with st.expander("View Recommendations", expanded=True):
        # Display images in a grid
        num_images = len(image_urls)
        images_per_row = 4
        rows = num_images // images_per_row + (1 if num_images % images_per_row != 0 else 0)
       
        for i in range(rows):
            row_html = '<div style="display:flex; flex-direction:row;">'
            for j in range(images_per_row):
                index = i * images_per_row + j
                if index < num_images:
                    url = image_urls[index]
                    brand = brands[index]
                    price = prices[index]
                    rating = ratings[index]
                    response = requests.get(url)
                    img = Image.open(BytesIO(response.content))
 
                    # Resize the image while maintaining aspect ratio
                    img.thumbnail((desired_width, desired_height))
                    width, height = img.size
                    aspect_ratio = width / height
 
                    # Adjust width and height based on aspect ratio
                    if aspect_ratio > 1:
                        new_width = desired_width
                        new_height = int(desired_width / aspect_ratio)
                    else:
                        new_width = int(desired_height * aspect_ratio)
                        new_height = desired_height
 
                    resized_image = img.resize((new_width, new_height))
 
                    output_buffer = BytesIO()
                    resized_image.save(output_buffer, format="JPEG")
                    resized_base64_data = base64.b64encode(output_buffer.getvalue()).decode("utf-8")
 
                    # Display image and URL below it
                    row_html += f'<div style="margin: 5px; text-align: center;">'
                    row_html += f'<img src="data:image/jpeg;base64,{resized_base64_data}" style="width:{new_width}px;height:auto;">'
                    row_html += f'<p style="font-weight: bold;">URL: <a href="{url}" target="_blank">{url}</a></p>'
                    if rec_type=="product":
                        row_html += f'<p style="font-weight: bold;">Brand: {brand}</p>'
                        row_html += f'<p style="font-weight: bold;">Price: ${price}</p>'
                        row_html += f'<p style="font-weight: bold;">Rating: {"⭐" * int(rating)}</p>'
                    else:
                        category = categories[index]
                        row_html += f'<p style="font-weight: bold;">Category: {category}</p>'
                        row_html += f'<p style="font-weight: bold;">Brand: {brand}</p>'

                    row_html += '</div>'
 
            row_html += '</div>'
            st.markdown(row_html, unsafe_allow_html=True)

with st.sidebar:

    with st.sidebar:
        selected = option_menu(
            menu_title = "Main Menu",
            options = ["About","App"])

if selected=="About":
    st.title("Retail Personalised Recommendation")

    st.write("""
    Welcome to the Retail Recommendation App! This application provides personalized product recommendations for customers based on their shopping history and preferences.
    """)

    st.header("Key Features:")
    st.markdown("""
    - **Personalized Recommendations:** Get product recommendations tailored to your preferences.
    - **Inspired by Shopping Trends:** Discover products inspired by your unique shopping history.
    - **User-Friendly Interface:** Easily navigate and interact with the app.
    """)

    st.header("How It Works:")
    st.markdown("""
    1. **User Selection:**
       - Choose a customer from the sidebar menu to view personalized recommendations.

    2. **Query Input:**
       - Enter a search query to get product recommendations or leave it empty for personalized suggestions.

    3. **Recommendations Display:**
       - View recommended products along with relevant information such as brand, price, and rating.

    4. **Explore and Shop:**
       - Click on product URLs to explore and shop the recommended items.

    5. **Inspired Recommendations:**
       - the app generates recommendations inspired by the user's shopping trends.

    Enjoy your personalized shopping experience with the Retail Recommendation App!
    """)


if selected=="App":
    with st.sidebar:
        selected_option = st.sidebar.selectbox(
            "Choose Your customer",
            ["", "Liam Mitchell", "Isla Harper", "Ethan Davies", "Ava Sullivan", "Oliver Williams"]
        )

    customer_mapping = {
        "Liam Mitchell": "Customer_1",
        "Isla Harper": "Customer_2",
        "Ethan Davies": "Customer_3",
        "Ava Sullivan": "Customer_4",
        "Oliver Williams": "Customer_5"
    }

    selected_customer = customer_mapping.get(selected_option, "")

    if selected_option and st.session_state.selected_user != selected_customer:
        st.session_state.selected_user = selected_customer
        st.session_state.query = ""
        
        # Modify URL parameters for selected user and empty query
        new_url_params = {"selected_option": selected_option, "query": ""}
        st.experimental_set_query_params(**new_url_params)

        st.experimental_rerun()

    if selected_customer=="Customer_1":
        df = pd.read_csv('GT_1k_data_with_description.csv')

        with st.sidebar:
            customer_1_data = df[df['user_name'] == 'Customer_1']

            # Extract unique values
            unique_brands = customer_1_data['brand'].unique().tolist()
            unique_categories = customer_1_data['category'].unique().tolist()

            st.markdown(f"**Name:**\n{selected_option}\n")
            st.markdown(f"**Gender:**\n{customer_1_data['gender'].iloc[0]}\n")
            st.markdown(f"**Location:**\n{customer_1_data['location'].iloc[0]}\n")

        st.title("Welcome Liam Mitchell")
        user_identifier = f"query_input_{selected_customer}"
        query_1 = st.text_input("Query", value=st.session_state.query, key=user_identifier)
        st.session_state.query = query_1

        if query_1:
            r_type="product"
            st.markdown("**Recommended for you**")

            image_urls, brands, ratings, prices, categories = product_vector_search(query_1)

            display_images_horizontal(image_urls, brands, prices, ratings, categories, r_type)

        else:
            r_type="personal"
            st.markdown("**Inspired by your shopping trends**")

            image_urls, brands, ratings, prices, categories = personal_vector_search(unique_categories,selected_customer)

            display_images_horizontal(image_urls, brands, prices, ratings, categories, r_type)

    if selected_customer=="Customer_2":
        df = pd.read_csv('GT_1k_data_with_description.csv')

        with st.sidebar:
            customer_1_data = df[df['user_name'] == 'Customer_2']

            # Extract unique values
            unique_brands = customer_1_data['brand'].unique().tolist()
            unique_categories = customer_1_data['category'].unique().tolist()

            st.markdown(f"**Name:**\n{selected_option}\n")
            st.markdown(f"**Gender:**\n{customer_1_data['gender'].iloc[5]}\n")
            st.markdown(f"**Location:**\n{customer_1_data['location'].iloc[5]}\n")

        st.title("Welcome Isla Harper")
        user_identifier = f"query_input_{selected_customer}"
        query_2 = st.text_input("Query", value=st.session_state.query,key=user_identifier)
        st.session_state.query = query_2

        if query_2:
            r_type="product"
            st.markdown("**Recommended for you**")

            image_urls, brands, ratings, prices, categories = product_vector_search(query_2)

            display_images_horizontal(image_urls, brands, prices, ratings, categories, r_type)

        else:
            r_type="personal"
            st.markdown("**Inspired by your shopping trends**")

            image_urls, brands, ratings, prices, categories = personal_vector_search(unique_categories,selected_customer)

            display_images_horizontal(image_urls, brands, prices, ratings, categories, r_type)

    if selected_customer=="Customer_3":
        df = pd.read_csv('GT_1k_data_with_description.csv')

        with st.sidebar:
            customer_1_data = df[df['user_name'] == 'Customer_3']

            # Extract unique values
            unique_brands = customer_1_data['brand'].unique().tolist()
            unique_categories = customer_1_data['category'].unique().tolist()

            st.markdown(f"**Name:**\n{selected_option}\n")
            st.markdown(f"**Gender:**\n{customer_1_data['gender'].iloc[4]}\n")
            st.markdown(f"**Location:**\n{customer_1_data['location'].iloc[4]}\n")

        st.title("Welcome Ethan Davies")
        user_identifier = f"query_input_{selected_customer}"
        query_3 = st.text_input("Query", value=st.session_state.query, key=user_identifier)
        st.session_state.query = query_3

        if query_3:
            r_type="product"
            st.markdown("**Recommended for you**")

            image_urls, brands, ratings, prices, categories = product_vector_search(query_3)

            display_images_horizontal(image_urls, brands, prices, ratings, categories, r_type)

        else:
            r_type="personal"
            st.markdown("**Inspired by your shopping trends**")

            image_urls, brands, ratings, prices, categories = personal_vector_search(unique_categories,selected_customer)

            display_images_horizontal(image_urls, brands, prices, ratings, categories, r_type)

    if selected_customer=="Customer_4":
        df = pd.read_csv('GT_1k_data_with_description.csv')

        with st.sidebar:
            customer_1_data = df[df['user_name'] == 'Customer_4']

            # Extract unique values
            unique_brands = customer_1_data['brand'].unique().tolist()
            unique_categories = customer_1_data['category'].unique().tolist()

            st.markdown(f"**Name:**\n{selected_option}\n")
            st.markdown(f"**Gender:**\n{customer_1_data['gender'].iloc[4]}\n")
            st.markdown(f"**Location:**\n{customer_1_data['location'].iloc[4]}\n")

        st.title("Welcome Ava Sullivan")
        user_identifier = f"query_input_{selected_customer}"
        query_4 = st.text_input("Query", value=st.session_state.query, key=user_identifier)
        st.session_state.query = query_4

        if query_4:
            r_type="product"
            st.markdown("**Recommended for you**")

            image_urls, brands, ratings, prices, categories = product_vector_search(query_4)

            display_images_horizontal(image_urls, brands, prices, ratings, categories, r_type)

        else:
            r_type="personal"
            st.markdown("**Inspired by your shopping trends**")

            image_urls, brands, ratings, prices, categories = personal_vector_search(unique_categories,selected_customer)

            display_images_horizontal(image_urls, brands, prices, ratings, categories, r_type)

    if selected_customer=="Customer_5":
        df = pd.read_csv('GT_1k_data_with_description.csv')

        with st.sidebar:
            customer_1_data = df[df['user_name'] == 'Customer_5']

            # Extract unique values
            unique_brands = customer_1_data['brand'].unique().tolist()
            unique_categories = customer_1_data['category'].unique().tolist()

            st.markdown(f"**Name:**\n{selected_option}\n")
            st.markdown(f"**Gender:**\n{customer_1_data['gender'].iloc[4]}\n")
            st.markdown(f"**Location:**\n{customer_1_data['location'].iloc[4]}\n")

        st.title("Welcome Oliver Williams")
        user_identifier = f"query_input_{selected_customer}"
        query_5 = st.text_input("Query", value=st.session_state.query,key=user_identifier)
        st.session_state.query = query_5

        if query_5:
            r_type="product"
            st.markdown("**Recommended for you**")

            image_urls, brands, ratings, prices, categories = product_vector_search(query_5)

            display_images_horizontal(image_urls, brands, prices, ratings, categories, r_type)
        
        else:
            r_type="personal"
            st.markdown("**Inspired by your shopping trends**")

            image_urls, brands, ratings, prices, categories = personal_vector_search(unique_categories,selected_customer)

            display_images_horizontal(image_urls, brands, prices, ratings, categories, r_type)