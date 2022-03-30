import base64
import os
import hypercorn.asyncio
from quart import Quart, jsonify, render_template_string, request
from quart_cors import cors
import asyncio
import logging
from telethon.tl.patched import MessageService
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon import TelegramClient
import pymongo
import uuid
import random
import copy.deepcopy as deepcopy
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
db_account = mydb["accounts"]
db_cate = mydb["categories"]
db_cate_world = mydb["categories_words"]
db_keyword = mydb["db_keyword"]
db_replaceword = mydb["db_replaceword"]
db_cate.drop()
db_account.drop()
mydict = { "id": str(uuid.uuid4().hex), "name": "coin", "type_id": "1", "cate_for": "account"}
db_cate.insert_one(mydict)
mydict = { "id": str(uuid.uuid4().hex), "name": "bit coin", "type_id": "2", "cate_for": "account"}
db_cate.insert_one(mydict)
mydict = { "id": str(uuid.uuid4().hex), "name": "Key Word", "type_id": "3", "cate_for": "filter"}
db_cate.insert_one(mydict)
mydict = { "id": str(uuid.uuid4().hex), "name": "Replace", "type_id": "4", "cate_for": "filter"}
db_cate.insert_one(mydict)

db_keyword.drop()
mydict = { "id": str(uuid.uuid4().hex), "keyword": "keyword", "category_id": "52d8151df4f344bba4b5c56974213dbd"}
db_keyword.insert_one(mydict)

mydict = { "id": str(uuid.uuid4().hex), "word": "keyword", "word": "asaasda", "category_id": "52d8151df4f344bba4b5c56974213dbd"}
db_replaceword.insert_one(mydict)
# mydict = { "id": "52d8151df4f344bba4b5c56974213dbd", "name": "BitCoin"}
# db_cate_world.insert_one(mydict)
db_task = mydb["tasks"]
db_task.insert_one({"id": "1", "name": "Crawl", "cate_for": "account"})
db_task.insert_one({"id": "2", "name": "Post", "cate_for": "account"})
db_task.insert_one({"id": "3", "name": "Key Word", "cate_for": "filter"})
db_task.insert_one({"id": "4", "name": "Replace", "cate_for": "filter"})

# tele_account = mydb["accounts"] 
def get_env(name, message):
    if name in os.environ:
        return os.environ[name]
    return input(message)

API_ID = "14225107" #os.getenv('api_id')
API_HASH = "bc6b2686eea4dc38f72181dd8d279dbf" #os.getenv('api_hash')
SESSION =  str(uuid.uuid4().hex)#os.getenv('STRING_SESSION')

# Render things nicely (global setting)
# Message.set_default_parse_mode('html')
#dict_client_crawl
##key: cat_id
##
client = None
phone = None
list_client = []
class TeleProcess:
    def __init__(self):
        self.categories_crawl = {}
        self.dict_client_crawl = {}
        self.dict_client_post = {}
        self.dict_crawls = {}
        self.dict_filter_words = {}
        self.dict_replace_words = {}
        self.dict_posts = {}
    def run(self):
        while 1:
            for k in deepcopy(self.categories_crawl).keys():
                category_crawl = self.categories_crawl.get(k)
                lst_clients = category_crawl.get("clients")
                client = None
                for cl in lst_clients:
                    if (cl is not None) or (await cl.is_user_authorized()):
                        client = cl
                        break
                if (client is None) or (not await client.is_user_authorized()): 
                    continue
                lst_from_chat = category_crawl.get("from_chats")
                for dict_from_chat in lst_dict_from_chat:
                    from_chat = dict_from_chat.get("from_chat")
                    offset = dict_from_chat.get("offset")
                    if not offset:
                        offset = 0

                    last_id = 0

                    async for message in client.iter_messages(intify(from_chat), reverse=True, offset_id=offset):
                        if isinstance(message, MessageService):
                            continue
                        try:
                            await client.send_message(intify(to_chat), message)
                            last_id = str(message.id)
                            logging.info('forwarding message with id = %s', last_id)
                            update_offset(forward, last_id)
                        except FloodWaitError as fwe:
                            print(f'{fwe}')
                            asyncio.sleep(delay=fwe.seconds)
                        except Exception as err:
                            logging.exception(err)
                            error_occured = True
                            break

