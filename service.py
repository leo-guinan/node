from decouple import config
from pymongo import MongoClient


def webhook_response():
    pass

# get all tools that are available. Tool should have name, description, url, output format, input required, and a pipe id

# get all tools from mongo:
def get_all_tools():
    mongo_client = MongoClient(config('MONGODB_CONNECTION_STRING'))
    db = mongo_client.agi
    for tool in db.tools.find():
        print(tool)


def add_tool(name, description, url, output_format, input_format, pipe_id):
    mongo_client = MongoClient(config('MONGODB_CONNECTION_STRING'))
    db = mongo_client.agi
    tool = db.tools.insert_one({
        "name": name,
        "description": description,
        "url": url,
        "output_format": output_format,
        "input_format": input_format,
        "pipe_id": pipe_id
    })
    return tool


def create_open_pipe():
    mongo_client = MongoClient(config('MONGODB_CONNECTION_STRING'))
    db = mongo_client.agi
    pipe = db.pipes.insert_one({
        "status": "open",
        "input_required": {
            "type": "text"
        },
        "output_required": {
            "type": "text"
        },
        "message_id": "1234",
        "initiator": "paul",
        "recipient": "leo",
        "webhook_url": "https://webhook.site/1234"


    })

    return pipe

