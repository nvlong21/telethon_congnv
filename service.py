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
def get_env(name, message):
    if name in os.environ:
        return os.environ[name]
    return input(message)

API_ID = "14225107" #os.getenv('api_id')
API_HASH = "bc6b2686eea4dc38f72181dd8d279dbf" #os.getenv('api_hash')
SESSION =  str(uuid.uuid4().hex)#os.getenv('STRING_SESSION')

class TeleProcess:
    def __init__(self):
        self.categories_crawl = {}
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.initial_crawl())

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


                lst_post_to = []
                post_to_query = {}
                if category_post_id!=ALL_CATEGORIES:
                    post_to_query.update({"category_id": category_post_id})
                lst_post_entri = DB_POST.find(post_to_query)
                for post_entri in lst_post_entri:
                    post_to = post_entri.get("post_to")
                    lst_post_to.append(post_to)
                
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
                    "post_to": lst_post_to,
                    "replaces": lst_replace_word
                })
            self.categories_crawl[cate_id]["from_chats"] = lst_dict_crawl
        print(self.categories_crawl)
        await asyncio.sleep(1)
    # def initial_post(self):
    #     categories_post = DB_CATEGORIES.find({"type_id": str(POSTER)})
    #     for category in list(categories_post):
    #         cate_id = category.get("id")
    #         self.categories_post[cate_id] = {}
    #         lst_client_crawl = DB_ACCOUNT.find({"category_id": cate_id})
    #         list_client = []
    #         for sess in lst_client_crawl:
    #             session_name = sess["name"]
    #             cl = TelegramClient(session_name, API_ID, API_HASH)
    #             await cl.connect()
    #             if await cl.is_user_authorized():
    #                 list_client.append(cl)
    #             else:
    #                 query = { "name":  session_name}
    #                 new_values = { "$set": { "status": 0 } }
    #                 status = DB_ACCOUNT.update_many(query, new_values)
    #         self.categories_crawl[cate_id]["clients"] = list_client
    #         craw_query = {}
    #         if cate_id!=ALL_CATEGORIES:
    #             craw_query = {"category_id": cate_id}

    #         lst_crawl = DB_CRAWL.find(craw_query)
    #         lst_dict_crawl = []

    #         for crawl in lst_crawl:
    #             from_chat = crawl.get("from")
    #             type_from = crawl.get("type")
    #             category_filter_id = crawl.get("keyword_id")
    #             offset = crawl.get("offset")
    #             lst_filter = []
    #             filter_query = {"type_id": str(KEY_WORDS)}
    #             if cate_id!=ALL_CATEGORIES:
    #                 filter_query.update({"id": category_filter_id})
    #             lst_categories_filter = DB_CATEGORIES.find(filter_query)
    #             for cate_filter in lst_categories_filter:
    #                 cate_category_filter_id = cate_filter.get("id")
    #                 filter_entri = DB_KEYWORD.find({"category_id": cate_category_filter_id})
    #                 str_filter = filter_entri.find("keyword")
    #                 lst_filter.append(str_filter)
    #             lst_dict_crawl.append({
    #                 "from_chat": from_chat,
    #                 "type": type_from,
    #                 "offset": offset,
    #                 "filters": lst_filter
    #             })
    #         self.categories_crawl[cate_id]["from_chats"] = lst_dict_crawl



    async def Crawl(self):
        while 1:
            time.sleep(1)
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
                lst_dict_from_chat = category_crawl.get("from_chats")
                for dict_from_chat in lst_dict_from_chat:
                    from_chat = dict_from_chat.get("from_chat")
                    offset = dict_from_chat.get("offset")
                    filters = dict_from_chat.get("filters")
                    lst_post_to = dict_from_chat.get("post_to")
                    replaces = dict_from_chat.get("replaces")
                    if not offset:
                        offset = 0
                    last_id = 0

                    async for message in client.iter_messages(intify(from_chat), reverse=True, offset_id=offset, offset_date=datetime.now()):
                        if isinstance(message, MessageService):
                            continue
                        print(message)
                        # try:
                        #     await client.send_message(intify(to_chat), message)
                        #     last_id = str(message.id)
                        #     logging.info('forwarding message with id = %s', last_id)
                        #     update_offset(forward, last_id)
                        # except FloodWaitError as fwe:
                        #     print(f'{fwe}')
                        #     asyncio.sleep(delay=fwe.seconds)
                        # except Exception as err:
                        #     logging.exception(err)
                        #     error_occured = True
                        #     break

tele = TeleProcess()

asyncio.run(tele.Crawl())
