from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Milvus
import openai

HOST = "prod-milvus-milvus.vector-db.svc.cluster.local"
PORT = "19530"
MILVUS_USERNAME = "username"
MILVUS_PASSWORD = "password"
COLLECTION_NAME = "samiksha_Retail_RecSys_1k_data_demo_collection"
OPENAI_API_KEY = ""

def product_vector_search(query):

    # init params
    image_urls = []
    brands = []
    ratings = []
    prices = []
    categories = []

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    vector_store = Milvus(
        embeddings,
        connection_args={"host": HOST, "port": PORT, 'user': MILVUS_USERNAME, 'password': MILVUS_PASSWORD},
        collection_name = COLLECTION_NAME,
        search_params = {"metric":"L2","index_type":"FLAT","offset":0},
        )

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

    vector_store = Milvus(
        embeddings,
        connection_args={"host": HOST, "port": PORT, 'user': MILVUS_USERNAME, 'password': MILVUS_PASSWORD},
        collection_name = COLLECTION_NAME,
        search_params = {"metric":"L2","index_type":"FLAT","offset":0},
        )

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
