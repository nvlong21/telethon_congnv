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
from loguru import logger
from  copy import deepcopy 
import time
from multiprocessing.dummy import Process, Queue
import re
import threading
from kafka import KafkaConsumer, KafkaProducer
from kafka.coordinator.assignors.range import RangePartitionAssignor
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
import socket
from kafka.structs import OffsetAndMetadata, TopicPartition
from kafka.admin import KafkaAdminClient, NewTopic



import json
logger.add("logs/crawl/{time:YYYY-MM-DD}_1.log", rotation="500 MB")
def get_env(name, message):
    if name in os.environ:
        return os.environ[name]
    return input(message)

API_ID = "14225107" #os.getenv('api_id')
API_HASH = "bc6b2686eea4dc38f72181dd8d279dbf" #os.getenv('api_hash')
SESSION =  str(uuid.uuid4().hex)#os.getenv('STRING_SESSION')
bootstrap_servers = get_env("BOOTSTRAP_SERVER", "localhost:9092")
partition_assignment_strategy = [
                RangePartitionAssignor,
                RoundRobinPartitionAssignor]
admin_client = None
try:
    admin_client = KafkaAdminClient(
        bootstrap_servers=bootstrap_servers, 
        client_id="{}".format(socket.gethostname())
    )

    topic_list = []
    topic_list.append(NewTopic(name="topic", num_partitions=1, replication_factor=1))
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
except:
    pass
finally:
    if admin_client is not None:
        admin_client.close()
def intify(string):
    try:
        return int(string)
    except:
        return string

def process_message(message, filters, stop_words, replaces):
    content = message.text
    
    filter_flag = False
    if len(filters)==0 or len(stop_words)==0:
        filter_flag = True
    else:
        for str_filter in filters:
            if str_filter.lower() in content.lower():
                filter_flag = True
                break
            
        for stop_word in stop_words:
            if stop_word.lower() in content.lower():
                filter_flag = False
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

CLIENTS = {}
CATEGORY_CRAWL = {}
CATEGORY_POST = {}
QUEUE_MESS =  Queue(maxsize = 100)
INIT = False
SENDING = False
async def initial_crawl():
    # if RUNNING
    global CLIENTS
    global CATEGORY_CRAWL
    CATEGORY_CRAWL_TEMP = {}
    categories_crawl = DB_CATEGORIES.find({"type_id": str(CRAWL)})
    
    for category in list(categories_crawl):
        cate_id = category.get("id")
        CATEGORY_CRAWL_TEMP[cate_id] = {}
        lst_client_crawl = DB_ACCOUNT.find({"category_id": cate_id})
        list_client = []
        for sess in lst_client_crawl:
            session_phone = sess["phone"]
            cl = CLIENTS.get(session_phone)
            if cl is None:
                cl = TelegramClient(session_phone, API_ID, API_HASH)
            try:
                await cl.connect()
            except Exception as e:
                logger.error(str(e))

            if await cl.is_user_authorized():
                list_client.append((session_phone, cl))
                
                CLIENTS[session_phone] = cl
                logger.info("Client {} activate!".format(str(session_phone)))
            else:
                query = { "phone":  session_phone}
                new_values = { "$set": { "status": "not author" } }
                status = DB_ACCOUNT.update_many(query, new_values)
                logger.info("Client {} not author!".format(str(session_phone)))
            
        CATEGORY_CRAWL_TEMP[cate_id]["clients"] = list_client
        craw_query = {}
        if cate_id!=ALL_CATEGORIES_CRAWL:
            craw_query = {"category_id": cate_id}
        
        lst_crawl = DB_CRAWL.find(craw_query)
        lst_dict_crawl = []
        for crawl in lst_crawl:
            id = crawl.get("id")
            from_chat = crawl.get("from")
            type_from = crawl.get("type")
            category_filter_id = crawl.get("category_keyword_id")
            category_stopwords_id = crawl.get("category_stopword_id")
            category_post_id = crawl.get("category_post_id")
            category_replace_id = crawl.get("category_replace_id")
            offset = crawl.get("offset")
            lst_filter = []
            filter_query = {}
            if category_filter_id!=ALL_CATEGORIES_FILTER:
                filter_query.update({"category_id": category_filter_id})
            lst_filter_entri = DB_KEYWORD.find(filter_query)
            for filter_entri in lst_filter_entri:
                str_filter = filter_entri.get("keyword")
                lst_filter.append(str_filter)

            lst_stopwords = []
            stopword_query = {}
            if category_stopwords_id!=ALL_CATEGORIES_STOP:
                stopword_query.update({"category_id": category_stopwords_id})
            lst_stopwords_entri = DB_STOPWORD.find(stopword_query)
            for stopword_entri in lst_stopwords_entri:
                str_filter = stopword_entri.get("stop_word")
                if str_filter is not None:
                    lst_stopwords.append(str_filter)


            lst_post_to_category = []
            lst_post_to_category.append(category_post_id)
            post_to_query = {"type_id":str(POSTER)}
            if category_post_id!=ALL_CATEGORIES_POST:
                post_to_query.update({"id": category_post_id})

            lst_category_entri = DB_CATEGORIES.find(post_to_query)
            for post_category_id in lst_category_entri:
                post_category_id = post_category_id.get("id")
                if post_category_id not in lst_post_to_category:
                    lst_post_to_category.append(post_category_id)
            
            lst_replace_word = []
            replace_word_query = {}
            if category_replace_id!=ALL_CATEGORIES_REPLACE:
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
                "stop_words": lst_stopwords,
                "post_to_category": lst_post_to_category,
                "replaces": lst_replace_word
            })
        CATEGORY_CRAWL_TEMP[cate_id]["from_chats"] = lst_dict_crawl
    logger.info("initial crawl done")
    categories_keys = list(CATEGORY_CRAWL_TEMP.keys()).copy()
    for k in categories_keys:
        CATEGORY_CRAWL[k] = {
            "clients": CATEGORY_CRAWL_TEMP[k]["clients"].copy(),
            "from_chats": deepcopy(CATEGORY_CRAWL_TEMP[k].get("from_chats"))
        }
    await asyncio.sleep(0.1)

async def Crawl():
    global CATEGORY_CRAWL
    global CLIENTS
    prediction_producer = KafkaProducer(bootstrap_servers= [bootstrap_servers],
                        value_serializer=lambda value: json.dumps(value).encode())
    last_activate_check = datetime.now()
    INIT = False
    while True:
        if (datetime.now() - last_activate_check).seconds > 10:
            temp = DB_LOG.find_one({"name": "reload"})
            INIT = str(temp["status_crawl"]) == "0"
            new_dict = { "$set": {"status_crawl": "0"}}
            query = { "name": "reload"}
            DB_LOG.update_many(query, new_dict)
            last_activate_check = datetime.now()
            
        if not INIT:
            for k in CLIENTS.keys():
                try:
                    await CLIENTS[k].disconnect()
                except:
                    logger.info("Disconnect client {} ".format(str(k)))
            await initial_crawl()
            INIT = True

        categories_keys = list(CATEGORY_CRAWL.keys()).copy()
        if len(categories_keys)==0:
            await initial_crawl()
            await asyncio.sleep(3)
        for k in CATEGORY_CRAWL.keys():
            category_crawl = CATEGORY_CRAWL[k]
            lst_clients = category_crawl.get("clients")
            if len(lst_clients) == 0:
                continue
            client = None
            temp_list = lst_clients.copy()
            i_s = 0
            for (phone_key, cl) in temp_list:
                if not cl.is_connected:
                    await cl.connect()

                if (cl is not None) or (await cl.is_user_authorized()):
                    client = cl
                    break
                else:
                    lst_clients.pop(i_s)
                    filter = { 'phone': phone_key }
                    newvalues = { "$set": {"status": "not author" } }
                    DB_ACCOUNT.update_one(filter, newvalues)
                i_s += 1

            category_crawl["clients"] = lst_clients
            if client is None: 
                logger.error("All crawl client is not activate")
                continue

            lst_dict_from_chat = category_crawl["from_chats"]
            
            for dict_from_chat in lst_dict_from_chat:
                id = dict_from_chat.get("id")
                from_chat = dict_from_chat.get("from_chat")
                offset = int(dict_from_chat.get("offset"))
                filters = dict_from_chat.get("filters")
                stop_words = dict_from_chat.get("stop_words")
                lst_post_to_category = dict_from_chat.get("post_to_category")
                replaces = dict_from_chat.get("replaces")
                if not offset:
                    offset = 0
                
                try:
                    count = 0
                    async for message in client.iter_messages(intify(from_chat), reverse=True, offset_id=offset):
                        dict_from_chat["offset"] = message.id
                        logger.info("Crawl from {} offset {}".format(from_chat, message.id))
                        
                        if isinstance(message, MessageService):
                            continue
                        if message.photo:
                            continue
                        content = process_message(message, filters, stop_words, replaces)
                        if content =="":
                            continue
                        message.text = "[{}] ".format(intify(from_chat)) + content
                        
                        try:
                            prediction_producer.send("topic",
                                                        value = {
                                                        "categories_id": lst_post_to_category,
                                                        "content": content
                                                    })
                            filter = { 'id': id }
                            newvalues = { "$set": { "offset": message.id} }
                            DB_CRAWL.update_one(filter, newvalues)
                            count += 1
                            if count>100:
                                break
                        except Exception as e1:
                            logger.error("{}".format(str(e1)))
                        await asyncio.sleep(1.5)
                        if not INIT:
                            break
                    await asyncio.sleep(1)
                    if not INIT:
                        break    
                except Exception as e:
                    logger.error("Crawl from {} error {}".format(from_chat, str(e)))
        await asyncio.sleep(0.1)
        
def run_init():
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(Crawl())
        # loop.run_until_complete(initial_post())
run_init()