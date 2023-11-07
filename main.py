import json
import uuid
from datetime import date
from functools import lru_cache
from typing import Annotated

import chromadb
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from pymongo import MongoClient
# import
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader

from decouple import config as dc_config

import config
from agent import shared

mongo_client = MongoClient(dc_config('MONGODB_CONNECTION_STRING'))
db = mongo_client.agi


@lru_cache
def get_settings():
    return config.Settings()

app = FastAPI()
class Data(BaseModel):
    message: str

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

    conversation = {
        "uuid": str(uuid.uuid4()),
        "messages": [
            {
            "speaker": "human",
            "text": data.message

            }
        ]
    }

    response = shared(data.message)

    conversation["messages"].append({
        "speaker": "bot",
        "text": response
    })

    remember(json.dumps(conversation))
    db.conversations.insert_one(conversation)
    return response

@app.post("/upload")
def upload_file(request):
    # Get JSON data from request
    data = request.json
    print("Data:", data)

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
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # load it into Chroma
    client = chromadb.HttpClient(host='db', port=8000)
    client.reset()  # resets the database
    collection = client.create_collection("my_collection")
    for doc in docs:
        collection.add(
            ids=[str(uuid.uuid1())], metadatas=[{"text": doc, "date": str(date.today()), "context": "work"}], documents=[doc]
        )

    # tell LangChain to use our client and collection name
    db4 = Chroma(
        client=client,
        collection_name="my_collection",
        embedding_function=embedding_function,
    )
    query = "What needs to be done and by when?"
    docs = db4.similarity_search(query)
    print(docs[0].page_content)