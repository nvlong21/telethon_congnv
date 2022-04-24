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
logger.add("logs/post/{time:YYYY-MM-DD}_1.log", rotation="500 MB")
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
# process_message("Long 0986626975 Spa Ha Noi vanlong@123", ["Long"], [{"word": "0[0-9\s.-]{9,13}", "replace": "123456789"}, 
#                                                             {"word": "Spa Ha Noi", "replace": "Anh Long"}])

    # return '<p><strong>{}</strong>: {}<sub>{}</sub></p>'.format(
    #     utils.get_display_name(message.sender),
    #     content,
    #     message.date
    # )
CLIENTS = {}
CATEGORY_CRAWL = {}
CATEGORY_POST = {}
QUEUE_MESS =  Queue(maxsize = 100)
INIT = False
SENDING = False

async def initial_post():
    # if RUNNING
    global CLIENTS
    global CATEGORY_CRAWL
    global CATEGORY_POST
    CATEGORY_POST_TEMP = {}
    categories_post = DB_CATEGORIES.find({"type_id": str(POSTER)})
    for category in list(categories_post):
        cate_id = category.get("id")
        CATEGORY_POST_TEMP[cate_id] = {}
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
                logger.info("Client {} activate!".format(str(session_phone)))
                list_client.append((session_phone, cl))
                CLIENTS[session_phone] = cl
            else:
                query = { "phone":  session_phone}
                new_values = { "$set": { "status": "not author" } }
                status = DB_ACCOUNT.update_many(query, new_values)
                logger.info("Client {} not author!".format(str(session_phone)))
        CATEGORY_POST_TEMP[cate_id]["clients"] = list_client
        post_to_query = {}
        if cate_id!=ALL_CATEGORIES_POST:
            post_to_query = {"category_id": cate_id}

        lst_post = DB_POST.find(post_to_query)
        lst_post_to = []
            
        for post_entrie in lst_post:
            post_to = post_entrie.get("post_to")
            if post_to not in lst_post_to:
                lst_post_to.append(post_to)
        
        CATEGORY_POST_TEMP[cate_id]["post_to"] = lst_post_to
    categories_keys = list(CATEGORY_POST_TEMP.keys()).copy()

    logger.info("initial post done")
    for k in categories_keys:
        CATEGORY_POST[k] = {
            "clients": CATEGORY_POST_TEMP[k]["clients"].copy(),
            "post_to": deepcopy(CATEGORY_POST_TEMP[k].get("post_to"))
        }
    await asyncio.sleep(0.1)
    

async def Sender():
    global CATEGORY_POST
    global INIT
    consumer = KafkaConsumer(group_id = "{}a".format(socket.gethostname()), client_id="{}".format(socket.gethostname()),
                                       bootstrap_servers=  [bootstrap_servers], # "10.68.10.95:9092", #self.bootstrap_servers,#
                                    #    key_deserializer=lambda key: key.decode(),
                                       value_deserializer=lambda value: json.loads(value.decode()),
                                       partition_assignment_strategy=partition_assignment_strategy,
                                       auto_offset_reset="earliest", api_version = (0, 10, 1))
    # # consumer.assign([TopicPartition('topic', 2)])
    consumer.subscribe("topic")
    producer = KafkaProducer(bootstrap_servers= [bootstrap_servers],
                        value_serializer=lambda value: json.dumps(value).encode())
    last_activate_check = datetime.now()
    INIT = False
    while 1:
        
        if (datetime.now() - last_activate_check).seconds > 10:
            temp = DB_LOG.find_one({"name": "reload"})
            INIT = temp["status_sender"] == 1
            new_dict = { "$set": {"status_sender": "0"}}
            query = { "name": "reload"}
            DB_LOG.update_many(query, new_dict)
            last_activate_check = datetime.now()
        if not INIT:
            for k in CLIENTS.keys():
                try:
                    await CLIENTS[k].disconnect()
                except:
                    logger.info("Disconnect client {} ".format(str(k)))
            await initial_post()
            await asyncio.sleep(1.5)
            INIT = True
            continue
        
        categories_keys = list(CATEGORY_POST.keys()).copy()
        categories_cp = {}
        try:
            raw_messages = consumer.poll(timeout_ms=100, max_records=10)
            
            # message = QUEUE_MESS.get_nowait()
            await asyncio.sleep(0.1)
            for _, msgs in raw_messages.items():
                for msg in msgs:
                    message = msg.value
                    categories_id = message.get("categories_id")
                    content = message.get("content")
                    
                    list_miss_category = []
                    for k in categories_id:
                        category_post = CATEGORY_POST.get(k)
                        lst_clients = category_post.get("clients")
                        lst_post_to = category_post.get("post_to")
                        client1 = None
                        temp_list = lst_clients.copy()
                        i_s = 0
                        for (phone_key, cl) in temp_list:
                            if (cl is not None) or (await cl.is_user_authorized()):
                                client1 = cl
                                break
                            else:
                                lst_clients.pop(i_s)
                                filter = { 'phone': phone_key }
                                newvalues = { "$set": {"status": "not author" } }
                                DB_ACCOUNT.update_one(filter, newvalues)
                            i_s += 1
                        category_post["clients"] = lst_clients
                        if client1 is None:
                            logger.info("All send client is not activate!")
                            list_miss_category.append(k)
                            await asyncio.sleep(5)
                            continue
                        if len(lst_post_to) ==0: 
                            logger.info("No chanel to post!")
                            await asyncio.sleep(5)
                            continue
                        for post_to in lst_post_to:
                            try:
                                # async with client1:
                                await client1.send_message(intify(post_to), content)
                                await asyncio.sleep(1.3)
                                logger.info("Send to {} content {}".format(intify(post_to), content))
                                # update_offset(forward, last_id)
                            except FloodWaitError as fwe:
                                logger.error(fwe)
                                asyncio.sleep(delay=fwe.seconds)
                            except Exception as err:
                                logger.error(err)
                                error_occured = True
                                break
                    if len(list_miss_category) >0:
                        producer.send("topic", value = {"categories_id": list_miss_category,
                                                        "content": content
                                                    })
                        await asyncio.sleep(0.5)
        except Exception as e:
            print("asdas: ", raw_messages)
            await asyncio.sleep(1.3)
            continue
        # for k in categories_keys:
        #     categories_cp[k] = {
        #         "clients": CATEGORY_POST[k]["clients"].copy(),
        #         "post_to": deepcopy(CATEGORY_CRAWL[k].get("post_to"))
        #     }
        SENDING = False
        
    await asyncio.sleep(0.1)
     
def run_init():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(Sender())
run_init()