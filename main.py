from __future__ import annotations

import json
import logging
import uuid
from datetime import date
from functools import lru_cache

import chromadb
import requests
from fastapi import FastAPI, Depends
from langchain.chains import LLMChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms.openai import OpenAI
from langchain.memory import ReadOnlySharedMemory, ConversationBufferMemory
from langchain.prompts import PromptTemplate
from pydantic import BaseModel
from pymongo import MongoClient
# import
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

from decouple import config as dc_config

import config
from agent import shared

mongo_client = MongoClient(dc_config('MONGODB_CONNECTION_STRING'))
db = mongo_client.agi
logger = logging.getLogger(__name__)

class WebhookBody(BaseModel):
    name: str


@lru_cache
def get_settings():
    return config.Settings()

app = FastAPI()
class Data(BaseModel):
    message: str
    respond_to: str = None

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/ask")
async def ask():

    # do I know locally? Answer

    # ask from chroma

    # does the answer answer the question?



    # if not, do I know who might know?

    # if not, ask the marketplace.


    return {"message": "I don't know"}


@app.post("/tell")
async def tell(data: Data):
    logger.info("Data:", data)
    conversation = {
        "uuid": str(uuid.uuid4()),
        "messages": [
            {
            "speaker": "human",
            "text": data.message

            }
        ]
    }

    logger.info(f"Processing message: {data.message}")

    response = shared(data.message)

    conversation["messages"].append({
        "speaker": "bot",
        "text": response
    })

    logger.info("Remembering conversation")
    remember(json.dumps(conversation))

    logger.info("Saving conversation")
    db.conversations.insert_one(conversation)

    if data.respond_to:
        logger.info("Responding to webhook")
        requests.post(data.respond_to, json={
            "message": response
        })
    return {"message": response}

@app.post("/upload")
def upload_file(request):
    # Get JSON data from request
    data = request.json
    logger.info("Data:", data)

    # Check for file in request
    if "file" in request.files:
        file = request.files["file"]
        filename = file.filename
        # Save the file or do something with it...
        file.save(f"uploads/{filename}")
        return f"File {filename} uploaded successfully!"

    return "No file uploaded."

def delete_context(request):
    pass


def remember(text):
    # load the document and split it into chunks


    # split it into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_text(text)

    # create the open-source embedding function
    embedding_function = OpenAIEmbeddings(openai_api_key=dc_config("OPENAI_API_KEY"))

    # load it into Chroma
    client = chromadb.HttpClient(host=dc_config("CHROMADB_HOST"), port=dc_config("CHROMADB_PORT"))
    chroma = Chroma(client=client, collection_name="my_collection", embedding_function=embedding_function)
    ids = []
    metadatas = []
    documents = []

    for doc in docs:
        ids.append(str(uuid.uuid1()))
        metadatas.append({"text": doc, "date": str(date.today()), "context": "work"})
        documents.append(doc)

    chroma.add_texts(documents, metadatas=metadatas, ids=ids)



    query = "What needs to be done and by when?"
    docs = chroma.similarity_search(query)
    logger.info(docs[0].page_content)

@app.post("/webhook/{webhook_uuid}")
async def webhook(webhook_uuid: str, body: WebhookBody):
    db.webhooks.insert_one({
        "uuid": webhook_uuid,
        "body": json.dumps(body)

    })

    return {"message": "ok"}