import os
from datetime import datetime
import asyncio
import logging
from telethon.tl.patched import MessageService
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon import TelegramClient, utils
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
        return '{}: {} - {}'.format(
                utils.get_display_name(message.sender),
                content,
                message.date)
    return ""
# process_message("Long 0986626975 Spa Ha Noi vanlong@123", ["Long"], [{"word": "0[0-9\s.-]{9,13}", "replace": "123456789"}, 
#                                                             {"word": "Spa Ha Noi", "replace": "Anh Long"}])

    # return '<p><strong>{}</strong>: {}<sub>{}</sub></p>'.format(
    #     utils.get_display_name(message.sender),
    #     content,
    #     message.date
    # )
CATEGORY_CRAWL = {}
CATEGORY_POST = {}
QUEUE_MESS =  Queue(maxsize = 100)

async def initial_crawl():
    print("initial_crawl")
    global CATEGORY_CRAWL
    global CATEGORY_POST

    categories_crawl = DB_CATEGORIES.find({"type_id": str(CRAWL)})
    for category in list(categories_crawl):
        cate_id = category.get("id")
        CATEGORY_CRAWL[cate_id] = {}
        lst_client_crawl = DB_ACCOUNT.find({"category_id": cate_id})
        list_client = []
        for sess in lst_client_crawl:
            session_phone = sess["phone"]
            cl = TelegramClient(session_phone, API_ID, API_HASH)
            await cl.connect()
            if await cl.is_user_authorized():
                list_client.append(cl)
            else:
                query = { "phone":  session_phone}
                new_values = { "$set": { "status": 0 } }
                status = DB_ACCOUNT.update_many(query, new_values)

        CATEGORY_CRAWL[cate_id]["clients"] = list_client

        craw_query = {}
        if cate_id!=ALL_CATEGORIES:
            craw_query = {"category_id": cate_id}

        lst_crawl = DB_CRAWL.find(craw_query)
        lst_dict_crawl = []

        for crawl in lst_crawl:
            id = crawl.get("id")
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
                if post_category_id not in lst_post_to_category:
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
                "id": id,
                "from_chat": from_chat,
                "type": type_from,
                "offset": offset,
                "filters": lst_filter,
                "post_to_category": lst_post_to_category,
                "replaces": lst_replace_word
            })
        CATEGORY_CRAWL[cate_id]["from_chats"] = lst_dict_crawl
    print("initial_crawl")
    await asyncio.sleep(0.1)

async def initial_post():
    global CATEGORY_CRAWL
    global CATEGORY_POST

    print("initial_post")
    categories_post = DB_CATEGORIES.find({"type_id": str(POSTER)})
    for category in list(categories_post):
        cate_id = category.get("id")
        CATEGORY_POST[cate_id] = {}
        lst_client_crawl = DB_ACCOUNT.find({"category_id": cate_id})
        list_client = []
        for sess in lst_client_crawl:
            session_phone = sess["phone"]
            
            cl = TelegramClient(session_phone, API_ID, API_HASH)
            await cl.connect()
            if await cl.is_user_authorized():
                print(session_phone)
                list_client.append(cl)
            else:
                query = { "phone":  session_phone}
                new_values = { "$set": { "status": 0 } }
                status = DB_ACCOUNT.update_many(query, new_values)
        CATEGORY_POST[cate_id]["clients"] = list_client
        post_to_query = {}
        if cate_id!=ALL_CATEGORIES:
            post_to_query = {"category_id": cate_id}

        lst_post = DB_POST.find(post_to_query)
        lst_post_to = []
            
        for post_entrie in lst_post:
            post_to = post_entrie.get("post_to")
            if post_to not in lst_post_to:
                lst_post_to.append(post_to)
        
        CATEGORY_POST[cate_id]["post_to"] = lst_post_to
    await asyncio.sleep(0.1)

async def Sender():
    global CATEGORY_CRAWL
    global CATEGORY_POST

    while 1:
        categories_keys = list(CATEGORY_POST.keys()).copy()
        categories_cp = {}
        try:
            message = QUEUE_MESS.get_nowait()
        except Exception as e:
            print("ex: ", e)
            await asyncio.sleep(1.3)
            continue
        # for k in categories_keys:
        #     categories_cp[k] = {
        #         "clients": CATEGORY_POST[k]["clients"].copy(),
        #         "post_to": deepcopy(CATEGORY_CRAWL[k].get("post_to"))
        #     }
        
        categories_id = message.get("categories_id")
        content = message.get("content")
        for k in categories_id:
            category_post = CATEGORY_POST.get(k)
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
                    # async with client1:
                    await client1.send_message(intify(post_to), content)
                    await asyncio.sleep(1.3)
                    print('forwarding message')
                    # update_offset(forward, last_id)
                except FloodWaitError as fwe:
                    print(f'{fwe}')
                    asyncio.sleep(delay=fwe.seconds)
                except Exception as err:
                    
                    logging.exception(err)
                    error_occured = True
                    break
        await asyncio.sleep(0.01)
            
async def Crawl():
    global CATEGORY_CRAWL
    global CATEGORY_POST

    while True:
        categories_keys = list(CATEGORY_CRAWL.keys()).copy()
        categories_cp = {}
        for k in categories_keys:
            categories_cp[k] = {
                "clients": CATEGORY_CRAWL[k]["clients"].copy(),
                "from_chats": deepcopy(CATEGORY_CRAWL[k].get("from_chats"))
            }
        for k in CATEGORY_CRAWL.keys():
            
            category_crawl = CATEGORY_CRAWL[k]
            lst_clients = category_crawl.get("clients")
            client = None
            for cl in lst_clients:
                if not cl.is_connected:
                    await cl.connect()
                if (cl is not None) or (await cl.is_user_authorized()):
                    client = cl
                    break
            if client is None: 
                print("send client is not activate")
                continue
            lst_dict_from_chat = category_crawl["from_chats"]
            for dict_from_chat in lst_dict_from_chat:
                id = dict_from_chat.get("id")
                from_chat = dict_from_chat.get("from_chat")
                offset = int(dict_from_chat.get("offset"))
                filters = dict_from_chat.get("filters")
                lst_post_to_category = dict_from_chat.get("post_to_category")
                replaces = dict_from_chat.get("replaces")
                if not offset:
                    offset = 0
                last_id = 0
                try:
                    async for message in client.iter_messages(intify("https://t.me/CoinMarketCap"), reverse=True, offset_id=offset):
                        # offset = str(message.id)
                        
                        dict_from_chat["offset"] = message.id
                        if isinstance(message, MessageService):
                            continue
                        if message.photo:
                            continue
                        content = process_message(message, filters, replaces)
                        if content =="":
                            continue
                        message.text = content
                        try:
                            QUEUE_MESS.put_nowait(
                                {
                                    "categories_id": lst_post_to_category,
                                    "content": content
                                })
                            filter = { 'id': id }
                            newvalues = { "$set": { "offset": message.id} }
                            DB_CRAWL.update_one(filter, newvalues)

                        except Exception as e:
                            print("asdada: ", e)
                        await asyncio.sleep(1.5)

                    print("a")
                except Exception as e:
                    print(e)
        await asyncio.sleep(1)
def run_init():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initial_crawl())
    loop.run_until_complete(initial_post())

# tele = TeleProcess()

# loop.run_forever()

# run(tele)
# run2(tele)target=analysis, args=("samplequery",)
# asyncio.run(Crawl())
# Process(target = asyncio.run(Crawl()), args=()).start()
# def run3(tele): 
#     async def main():
#         await asyncio.gather(
#             tele.Crawl(),
#             tele.Sender(),
#         )
#     loop = get_or_create_eventloop()
#     future = asyncio.ensure_future( main())
#     loop.run_until_complete(future)
# run3(tele) 
# asyncio.run(main())