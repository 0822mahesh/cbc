import nest_asyncio
import asyncio
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
import bs4
from slugify import slugify
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import json
from langchain_openai import OpenAIEmbeddings
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

nest_asyncio.apply() 
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")

#Base URL for editorial documents from webpage
base_url = "https://cbc.radio-canada.ca/en/vision/governance/journalistic-standards-and-practices/" 
not_read_urls = [
    "https://cbc.radio-canada.ca/en/vision/governance/journalistic-standards-and-practices/war-terror-natural-disasters",
    "https://cbc.radio-canada.ca/en/vision/governance/journalistic-standards-and-practices/Opinion",
    "https://cbc.radio-canada.ca/en/vision/governance/journalistic-standards-and-practices/user-generated-content",
    "https://cbc.radio-canada.ca/en/vision/governance/journalistic-standards-and-practices/Language"]

async def load_articles():
    try:
        with open("data/news-dataset.json", "r") as f:
            dataset = json.load(f)
        documents = []
        for item in dataset:
            article_id = item.get("content_id", "")
            headline = item.get("content_headline", "")
            content = f"Headline: {headline}\n\nCategories: {[c['content_category'] for c in item.get('content_categories', [])]}\n\nTags: {[t['name'] for t in item.get('content_tags', [])]}\n\nDepartment: {item.get('content_department_path')}"
            documents.append(Document(page_content=content, metadata={"id": article_id}))
        return documents
    except FileNotFoundError:
        logging.info("Json data file not found")
        return []
async def get_urls_from_web(base_url:str):
    try:
        #extracting titles and generating urls
        web_loader = AsyncChromiumLoader([base_url])
        html_info = web_loader.load()
        soup = bs4.BeautifulSoup(html_info[0].page_content)
        list_of_titles_tages=soup.find_all(["h3"])
        titles = set() # to avoid duplicate titles
        for _ in range(len(list_of_titles_tages)):
            titles.add(f"{base_url}{slugify(list_of_titles_tages[_].get_text())}")

        list_of_tiles=list(titles)
        return list_of_tiles
    except:
        logging.info(f"error while scraping baseurl {base_url}")
        return []



async def load_and_transform():
    try:
        list_of_tiles = await get_urls_from_web(base_url)
        list_of_tiles.extend(not_read_urls)
        loader = AsyncChromiumLoader(list_of_tiles)
        html_docs = loader.load()
        bs_transformer = BeautifulSoupTransformer()
        docs = bs_transformer.transform_documents(html_docs, tags_to_extract=["p", "h1", "h2", "h3"])
        return docs
    except:
        logging.info("error during tranforming the data to documents for embading")
        return []

# Run the async function
#docs = await load_and_transform(list_of_tiles)

def embadings_model():
    return OpenAIEmbeddings(model="text-embedding-3-large")

embeddings = embadings_model()

async def create_vectorstore():
    try:
        docs_from_web = await load_and_transform()
        docs_from_json = await load_articles()
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,)
        docs_spw = splitter.split_documents(docs_from_web)
        docs_json = splitter.split_documents(docs_from_json)
        docs_spw.extend(docs_json)
        vector_store = FAISS.from_documents(documents=docs_spw, embedding=embeddings)
        vector_store.save_local("cbc-index")
        logging.info("vector database created")
    except Exception as e:
        logging.info(f"error during vector store creation {e}")



if __name__ == "__main__":
    asyncio.run(create_vectorstore())