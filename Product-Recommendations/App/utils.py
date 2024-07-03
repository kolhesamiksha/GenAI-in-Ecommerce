from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Milvus
import openai

OPENAI_API_KEY = ""

def product_vector_search(query):

    # init params
    image_urls = []
    brands = []
    ratings = []
    prices = []
    categories = []

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    #TODO: add Qdrant Search Code

    recommendations = vector_store.similarity_search_with_score(query,k=8)

    for i, img_url in enumerate(recommendations):

        image_urls.append(img_url[0].metadata['image_url'])
        categories.append(img_url[0].metadata['category'])
        brands.append(img_url[0].metadata['brand'])
        ratings.append(img_url[0].metadata['ratings'])
        prices.append(img_url[0].metadata['price'])

    return image_urls, brands, ratings, prices, categories

def personal_vector_search(prev_category, user):

    # init params
    image_urls = []
    brands = []
    ratings = []
    prices = []
    categories = []

    embeddings = OpenAIEmbeddings(openai_api_key="")

    #TODO: add Qdrant Search Code

    query = f"Suggest me some products from categories like {prev_category}"
    recommendations = vector_store.similarity_search_with_score(query,k=12,expr=f'user_name=="{user}"')

    for i, img_url in enumerate(recommendations):

        image_urls.append(img_url[0].metadata['image_url'])
        categories.append(img_url[0].metadata['category'])
        brands.append(img_url[0].metadata['brand'])
        ratings.append(img_url[0].metadata['ratings'])
        prices.append(img_url[0].metadata['price'])

    return image_urls, brands, ratings, prices, categories
# Display images in a horizontal line
