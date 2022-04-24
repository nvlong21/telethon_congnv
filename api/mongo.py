import pymongo
import uuid
import os
MONGO = os.environ.get('MONGO', 'mongodb://localhost:27017/')
CRAWL = 1
POSTER = 2
KEY_WORDS = 3
REPLACE_WORDS = 4
STOP_WORDS = 5



COLLECTION = pymongo.MongoClient(MONGO)
DB_FORWARD_CHAT = COLLECTION["tele_forward_chat"]
ALL_CATEGORIES_POST = "52d8151df4f344bba4b5c56974213dbd"
ALL_CATEGORIES_CRAWL = "52d8151df4f344bba4b5c56974213bbd"
ALL_CATEGORIES_FILTER = "52d8151df4f344bba4b5c56974213fbd"
ALL_CATEGORIES_STOP = "52d8151df4f344bba4b5c56974213sbd"
ALL_CATEGORIES_REPLACE = "52d8151df4f344bba4b5c56974213rbd"
DB_ACCOUNT = DB_FORWARD_CHAT["accounts"]
DB_CATEGORIES = DB_FORWARD_CHAT["categories"]
DB_KEYWORD = DB_FORWARD_CHAT["keywords"]
DB_STOPWORD = DB_FORWARD_CHAT["stop_words"]
DB_REPLACE_WORD = DB_FORWARD_CHAT["replace_words"]
DB_CRAWL = DB_FORWARD_CHAT["crawls"]
DB_POST = DB_FORWARD_CHAT["posts"]
DB_TASK = DB_FORWARD_CHAT["tasks"]
DB_LOG = DB_FORWARD_CHAT["logs"]
# temp = DB_LOG.find_one({"name": "reload"})
# if temp is None:

new_dict = { "$set": {"status_crawl": "0", "status_sender": "0"}}
query = { "name": "reload"}
DB_LOG.update_many(query, new_dict)
temp = DB_TASK.find_one({"name": "Crawl"})
if temp is None:
    DB_TASK.insert_one({"id": str(CRAWL), "name": "Crawl", "cate_for": "account"})
temp = DB_TASK.find_one({"name": "Post"})
if temp is None:
    DB_TASK.insert_one({"id": str(POSTER), "name": "Post", "cate_for": "account"})
temp = DB_TASK.find_one({"name": "Key Word"})
if temp is None:
    DB_TASK.insert_one({"id": str(KEY_WORDS), "name": "Key Word", "cate_for": "filter"})
temp = DB_TASK.find_one({"name": "Replace"})
if temp is None:
    DB_TASK.insert_one({"id": str(REPLACE_WORDS), "name": "Replace", "cate_for": "filter"})
temp = DB_TASK.find_one({"name": "Stop Words"})
if temp is None:
    DB_TASK.insert_one({"id": str(STOP_WORDS), "name": "Stop Words", "cate_for": "filter"})


temp = DB_CATEGORIES.find_one({"id": ALL_CATEGORIES_CRAWL})
if temp is None:
    DB_CATEGORIES.insert_one({"id": str(ALL_CATEGORIES_CRAWL), "name": "All", "type_id": "1" })

temp = DB_CATEGORIES.find_one({"id": ALL_CATEGORIES_POST})
if temp is None:
    DB_CATEGORIES.insert_one({"id": str(ALL_CATEGORIES_POST), "name": "All", "type_id": "2" })


temp = DB_CATEGORIES.find_one({"id": ALL_CATEGORIES_FILTER})
if temp is None:
    DB_CATEGORIES.insert_one({"id": str(ALL_CATEGORIES_FILTER), "name": "All", "type_id": "3" })

temp = DB_CATEGORIES.find_one({"id": ALL_CATEGORIES_REPLACE})
if temp is None:
    DB_CATEGORIES.insert_one({"id": str(ALL_CATEGORIES_REPLACE), "name": "All", "type_id": "4" })

temp = DB_CATEGORIES.find_one({"id": ALL_CATEGORIES_STOP})
if temp is None:
    DB_CATEGORIES.insert_one({"id": str(ALL_CATEGORIES_STOP), "name": "All", "type_id": "5" })



def drop_all():
    DB_ACCOUNT.drop()
    DB_CATEGORIES.drop()
    DB_KEYWORD.drop()
    DB_REPLACE_WORD.drop()
    DB_CRAWL.drop()
    DB_TASK.drop()
    DB_POST.drop()
    DB_STOPWORD.drop()
    
# drop_all()
def test_db():
    mydict = { "id": str(uuid.uuid4().hex), "phone": "84925905936", "task_id": str(CRAWL), "category_id": "coin", "status": "live"}
    DB_ACCOUNT.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "phone": "84925899891", "task_id": str(CRAWL), "category_id": "coin", "status": "live"}
    DB_ACCOUNT.insert_one(mydict)
    mydict = { "id": str(uuid.uuid4().hex), "phone": "84925919435", "task_id": str(CRAWL), "category_id": "coin", "status": "live"}
    DB_ACCOUNT.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "phone": "84925926503", "task_id": str(CRAWL), "category_id": "trade", "status": "live"}
    DB_ACCOUNT.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "phone": "84925957599", "task_id": str(CRAWL), "category_id": "trade", "status": "live"}
    DB_ACCOUNT.insert_one(mydict)


    mydict = { "id": str(uuid.uuid4().hex), "phone": "84925967881", "task_id": str(POSTER), "category_id": "52d8151df4f344bba4b5c56974213dap", "status": "live"}
    DB_ACCOUNT.insert_one(mydict)


    mydict = { "id": str(uuid.uuid4().hex), "phone": "84925974502", "task_id": str(POSTER), "category_id": "52d8151df4f344bba4b5c56974213dap", "status": "live"}
    DB_ACCOUNT.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "phone": "84925982905", "task_id": str(POSTER), "category_id": "52d8151df4f344bba4b5c56974213dap", "status": "live"}
    DB_ACCOUNT.insert_one(mydict)


    mydict = { "id": str(uuid.uuid4().hex), "from": "https://t.me/CoinMarketCap", "type": "chanel", "category_id": "coin",
                "category_keyword_id": "52d8151df4f344bba4b5c56974213dac", "category_stopword_id" : "52d8151df4f344bba4b5c5697421", "category_post_id": "52d8151df4f344bba4b5c56974213dap",
                "category_replace_id": "52d8151df4f344bba4b5c56974213dar", "offset": 3300000}
    DB_CRAWL.insert_one(mydict)
    mydict = { "id": str(uuid.uuid4().hex), "from": "https://t.me/CoinDCX_Go_Announcements", "type": "chanel", "category_id": "coin",
                "category_keyword_id": "52d8151df4f344bba4b5c56974213dac", "category_stopword_id" : "52d8151df4f344bba4b5c5697421", "category_post_id": "52d8151df4f344bba4b5c56974213dap",
                "category_replace_id": "52d8151df4f344bba4b5c56974213dar", "offset": 0}
    DB_CRAWL.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "from": "https://t.me/coindcx", "type": "chanel", "category_id": "coin",
                "category_keyword_id": "52d8151df4f344bba4b5c56974213dac", "category_stopword_id" : "52d8151df4f344bba4b5c5697421", "category_post_id": "52d8151df4f344bba4b5c56974213dap",
                "category_replace_id": "52d8151df4f344bba4b5c56974213dar", "offset": 0}
    DB_CRAWL.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "from": "https://t.me/CoinX", "type": "chanel", "category_id": "coin",
                "category_keyword_id": "52d8151df4f344bba4b5c56974213dac", "category_stopword_id" : "52d8151df4f344bba4b5c5697421", "category_post_id": "52d8151df4f344bba4b5c56974213dap",
                "category_replace_id": "52d8151df4f344bba4b5c56974213dar", "offset": 0}
    DB_CRAWL.insert_one(mydict)


    mydict = { "id": str(uuid.uuid4().hex), "from": "https://t.me/FTX_Official", "type": "chanel", "category_id": "trade",
                "category_keyword_id": "52d8151df4f344bba4b5c56974213d", "category_stopword_id" : "52d8151df4f344bba4b5c5697421","category_post_id": "52d8151df4f344bba4b5c56974213dap",
                "category_replace_id": "52d8151df4f344bba4b5c56974213dar", "offset": 0}
    DB_CRAWL.insert_one(mydict)
    mydict = { "id": str(uuid.uuid4().hex), "from": "https://t.me/teleportstrader", "type": "chanel", "category_id": "trade",
                "category_keyword_id": "52d8151df4f344bba4b5c56974213d", "category_stopword_id" : "52d8151df4f344bba4b5c5697421","category_post_id": "52d8151df4f344bba4b5c56974213dap",
                "category_replace_id": "52d8151df4f344bba4b5c56974213dar", "offset": 0}
    DB_CRAWL.insert_one(mydict)
    mydict = { "id": str(uuid.uuid4().hex), "from": "https://t.me/trade", "type": "chanel", "category_id": "trade",
                "category_keyword_id": "52d8151df4f344bba4b5c56974213d", "category_stopword_id" : "52d8151df4f344bba4b5c5697421","category_post_id": "52d8151df4f344bba4b5c56974213dap",
                "category_replace_id": "52d8151df4f344bba4b5c56974213dar", "offset": 0}
    DB_CRAWL.insert_one(mydict)

    mydict = { "id": "coin", "name": "coin", "type_id": "1"}
    DB_CATEGORIES.insert_one(mydict)
    mydict = { "id": "trade", "name": "Bit coin", "type_id": "1"}
    DB_CATEGORIES.insert_one(mydict)

    mydict = { "id": "52d8151df4f344bba4b5c56974213dap", "name": "bit coin", "type_id": "2"}
    DB_CATEGORIES.insert_one(mydict)
    mydict = { "id": "52d8151df4f344bba4b5c56974213dac", "name": "Key Word", "type_id": "3"}
    DB_CATEGORIES.insert_one(mydict)
    mydict = { "id": "52d8151df4f344bba4b5c56974213d", "name": "Key Word Trade", "type_id": "3"}
    DB_CATEGORIES.insert_one(mydict)
    mydict = { "id": "52d8151df4f344bba4b5c56974213dar", "name": "Replace", "type_id": "4"}
    DB_CATEGORIES.insert_one(mydict)
    mydict = { "id": "52d8151df4f344bba4b5c5697421", "name": "Stop word for trade", "type_id": "5"}
    DB_CATEGORIES.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "keyword": "coin", "category_id": "52d8151df4f344bba4b5c56974213dac"}
    DB_KEYWORD.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "keyword": "Blockchain", "category_id": "52d8151df4f344bba4b5c56974213dac"}
    DB_KEYWORD.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "keyword": "USB", "category_id": "52d8151df4f344bba4b5c56974213d"}
    DB_KEYWORD.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "keyword": "ETH", "category_id": "52d8151df4f344bba4b5c56974213d"}
    DB_KEYWORD.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "keyword": "trade", "category_id": "52d8151df4f344bba4b5c56974213d"}
    DB_KEYWORD.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "stop_word": "123", "category_id": "52d8151df4f344bba4b5c5697421"}
    DB_STOPWORD.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "stop_word": "456", "category_id": "52d8151df4f344bba4b5c5697421"}
    DB_STOPWORD.insert_one(mydict)



    mydict = { "id": str(uuid.uuid4().hex), "word": "0[0-9\s.-]{9-13}", "replace": "0986626975", "category_id": "52d8151df4f344bba4b5c56974213dar"}
    DB_REPLACE_WORD.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "word": '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "replace": "long@gmail.com", "category_id": "52d8151df4f344bba4b5c56974213dar"}
    DB_REPLACE_WORD.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "post_to": "t.me/chaneltestcrawl1", "type": "chanel",  "category_id": "52d8151df4f344bba4b5c56974213dap"}
    DB_POST.insert_one(mydict)

    mydict = { "id": str(uuid.uuid4().hex), "post_to": "-1001553181857", "type": "chanel",  "category_id": "52d8151df4f344bba4b5c56974213dap"}
    DB_POST.insert_one(mydict)

    