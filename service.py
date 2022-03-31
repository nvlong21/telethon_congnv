import os
from datetime import datetime
import asyncio
import logging
from telethon.tl.patched import MessageService
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon import TelegramClient
from mongo import *
import uuid
import random

from  copy import deepcopy 
import time
from multiprocessing.dummy import Process, Queue
import re
import threading
# import nest_asyncio
# nest_asyncio.apply()
def get_env(name, message):
    if name in os.environ:
        return os.environ[name]
    return input(message)

API_ID = "14225107" #os.getenv('api_id')
API_HASH = "bc6b2686eea4dc38f72181dd8d279dbf" #os.getenv('api_hash')
SESSION =  str(uuid.uuid4().hex)#os.getenv('STRING_SESSION')
def intify(string):
    try:
        return int(string)
    except:
        return string

def process_message(message, filters, replaces):
    # if message.photo:
    #     content = '<img src="data:image/png;base64,{}" alt="{}" />'.format(
    #         base64.b64encode(await message.download_media(bytes)).decode(),
    #         message.raw_text
    #     )
    # else:
    #     # The Message parse_mode is 'html', so bold etc. will work!
    content = message.text
    filter_flag = False
    for str_filter in filters:
        if str_filter.lower() in content.lower():
            
            filter_flag = True
            break

    if filter_flag:
        for replace_dct in replaces:
            word =  replace_dct["word"]
            replace = replace_dct["replace"]
            content = re.sub(word, " " + replace + " ", content)
        return content
    return ""
# process_message("Long 0986626975 Spa Ha Noi vanlong@123", ["Long"], [{"word": "0[0-9\s.-]{9,13}", "replace": "123456789"}, 
#                                                             {"word": "Spa Ha Noi", "replace": "Anh Long"}])

    # return '<p><strong>{}</strong>: {}<sub>{}</sub></p>'.format(
    #     utils.get_display_name(message.sender),
    #     content,
    #     message.date
    # )

class TeleProcess:
    def __init__(self):
        self.categories_crawl = {}
        self.categories_post = {}
        self.queue_mess =  Queue(maxsize = 100)
    async def initial_crawl(self):
        print("initial_crawl")
        categories_crawl = DB_CATEGORIES.find({"type_id": str(CRAWL)})
        for category in list(categories_crawl):
            cate_id = category.get("id")
            self.categories_crawl[cate_id] = {}
            lst_client_crawl = DB_ACCOUNT.find({"category_id": cate_id})
            list_client = []
            for sess in lst_client_crawl:
                session_name = sess["name"]
                cl = TelegramClient(session_name, API_ID, API_HASH)
                await cl.connect()
                if await cl.is_user_authorized():
                    list_client.append(cl)
                else:
                    query = { "name":  session_name}
                    new_values = { "$set": { "status": 0 } }
                    status = DB_ACCOUNT.update_many(query, new_values)

            self.categories_crawl[cate_id]["clients"] = list_client

            craw_query = {}
            if cate_id!=ALL_CATEGORIES:
                craw_query = {"category_id": cate_id}

            lst_crawl = DB_CRAWL.find(craw_query)
            lst_dict_crawl = []

            for crawl in lst_crawl:
                from_chat = crawl.get("from")
                type_from = crawl.get("type")
                category_filter_id = crawl.get("category_keyword_id")
                category_post_id = crawl.get("category_post_id")
                category_replace_id = crawl.get("category_replace_id")
                offset = crawl.get("offset")
                lst_filter = []
                filter_query = {}
                if category_filter_id!=ALL_CATEGORIES:
                    filter_query.update({"category_id": category_filter_id})
                lst_filter_entri = DB_KEYWORD.find(filter_query)
                for filter_entri in lst_filter_entri:
                    str_filter = filter_entri.get("keyword")
                    lst_filter.append(str_filter)

                lst_post_to_category = []
                lst_post_to_category.append(category_post_id)
                post_to_query = {"type_id":str(POSTER)}
                if category_post_id!=ALL_CATEGORIES:
                    post_to_query.update({"id": category_post_id})

                lst_category_entri = DB_CATEGORIES.find(post_to_query)
                for post_category_id in lst_category_entri:
                    post_category_id = post_category_id.get("id")
                    lst_post_to_category.append(post_category_id)
                
                lst_replace_word = []
                replace_word_query = {}
                if category_replace_id!=ALL_CATEGORIES:
                    replace_word_query.update({"category_id": category_replace_id})

                lst_replace_word_entri = DB_REPLACE_WORD.find(replace_word_query)
                for replace_word_entri in lst_replace_word_entri:
                    word = replace_word_entri.get("word")
                    replace = replace_word_entri.get("replace")
                    lst_replace_word.append({"word": word,
                                            "replace": replace
                                            })
                lst_dict_crawl.append({
                    "from_chat": from_chat,
                    "type": type_from,
                    "offset": offset,
                    "filters": lst_filter,
                    "post_to_category": lst_post_to_category,
                    "replaces": lst_replace_word
                })
            self.categories_crawl[cate_id]["from_chats"] = lst_dict_crawl
        print("initial_crawl")
        await asyncio.sleep(0.1)

    async def initial_post(self):
        print("initial_post")
        categories_post = DB_CATEGORIES.find({"type_id": str(POSTER)})
        for category in list(categories_post):
            cate_id = category.get("id")
            self.categories_post[cate_id] = {}
            lst_client_crawl = DB_ACCOUNT.find({"category_id": cate_id})
            list_client = []
            for sess in lst_client_crawl:
                session_name = sess["name"]
                
                cl = TelegramClient(session_name, API_ID, API_HASH)
                await cl.connect()
                if await cl.is_user_authorized():
                    print(session_name)
                    list_client.append(cl)
                else:
                    query = { "name":  session_name}
                    new_values = { "$set": { "status": 0 } }
                    status = DB_ACCOUNT.update_many(query, new_values)
            self.categories_post[cate_id]["clients"] = list_client
            post_to_query = {}
            if cate_id!=ALL_CATEGORIES:
                post_to_query = {"category_id": cate_id}

            lst_post = DB_POST.find(post_to_query)
            lst_post_to = []
                
            for post_entrie in lst_post:
                post_to = post_entrie.get("post_to")
                lst_post_to.append(post_to)
            self.categories_post[cate_id]["post_to"] = lst_post_to
        await asyncio.sleep(0.1)

    async def Sender(self):
        while 1:
            categories_keys = list(self.categories_post.keys()).copy()
            categories_cp = {}
            message = self.queue_mess.get()
            # for k in categories_keys:
            #     categories_cp[k] = {
            #         "clients": self.categories_post[k]["clients"].copy(),
            #         "post_to": deepcopy(self.categories_crawl[k].get("post_to"))
            #     }

            categories_id = message.get("categories_id")
            content = message.get("content")
            for k in categories_id:
                category_post = self.categories_post.get(k)
                lst_clients = category_post.get("clients")
                client1 = None
                for cl in lst_clients:
                    if (cl is not None) or (await cl.is_user_authorized()):
                        client1 = cl
                        break
                if client1 is None: 
                    print("client is not activate")
                    continue
                lst_post_to = category_post.get("post_to")
                # client1.send_message("me", "content")
                for post_to in lst_post_to:
                    
                    try:
                        async with client1:
                            await client1.send_message("me", content)
                        
                        logging.info('forwarding message')
                        # update_offset(forward, last_id)
                    except FloodWaitError as fwe:
                        print(f'{fwe}')
                        asyncio.sleep(delay=fwe.seconds)
                    except Exception as err:
                        
                        logging.exception(err)
                        error_occured = True
                        break

            
    async def Crawl(self):
        while 1:
            await asyncio.sleep(0.01)
            print("a")
            categories_keys = list(self.categories_crawl.keys()).copy()
            categories_cp = {}
            for k in categories_keys:
                categories_cp[k] = {
                    "clients": self.categories_crawl[k]["clients"].copy(),
                    "from_chats": deepcopy(self.categories_crawl[k].get("from_chats"))
                }
            
            for k in  categories_cp.keys():
                category_crawl = categories_cp.get(k)
                lst_clients = category_crawl.get("clients")
                client = None
                for cl in lst_clients:
                    if (cl is not None) or (await cl.is_user_authorized()):
                        client = cl
                        break
                if client is None: 
                    print("client is not activate")
                    continue
                
                lst_dict_from_chat = category_crawl.get("from_chats")
                
                for dict_from_chat in lst_dict_from_chat:
                    from_chat = dict_from_chat.get("from_chat")
                    offset = dict_from_chat.get("offset")
                    filters = dict_from_chat.get("filters")
                    lst_post_to_category = dict_from_chat.get("post_to_category")
                    replaces = dict_from_chat.get("replaces")
                    if not offset:
                        offset = 0
                    last_id = 0
                    
                    async for message in client.iter_messages(intify(from_chat), reverse=True, offset_id=offset):
                        if isinstance(message, MessageService):
                            continue
                        print('Working with')
                        # content = process_message(message, filters, replaces)
                        # message.text = content + "1"
                        self.queue_mess.put(
                            {
                                "categories_id": lst_post_to_category,
                                "content": message
                            })
                        await asyncio.sleep(0.1)
                       
                        # try:
                        #     await client.send_message(intify("me"), message)
                        #     print("asad", client)
                        # except FloodWaitError as fwe:
                        #     print(f'{fwe}')
                        #     asyncio.sleep(delay=fwe.seconds)
                        # except Exception as err:
                        #     logging.exception(err)
                        #     error_occured = True
                        #     break

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()
def run(tele): 
    print("asda")
    loop = get_or_create_eventloop()
    future = asyncio.ensure_future(tele.Crawl())
    loop.run_until_complete(future)
def run2(tele): 
    print("asda")
    loop = get_or_create_eventloop()
    future = asyncio.ensure_future(tele.Sender())
    loop.run_until_complete(future)


async def main():
    tele = TeleProcess()

    await asyncio.gather(
        tele.initial_crawl(),
        tele.initial_post(),
        tele.Crawl(),
        tele.Sender(),
    )
asyncio.run(main())