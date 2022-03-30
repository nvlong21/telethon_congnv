import pymongo
import uuid
CRAWL = 1
POSTER = 2
KEY_WORDS = 3
REPLACE_WORDS = 4


COLLECTION = pymongo.MongoClient("mongodb://localhost:27017/")
DB_FORWARD_CHAT = COLLECTION["tele_forward_chat"]
ALL_CATEGORIES = "52d8151df4f344bba4b5c56974213dbd"

DB_ACCOUNT = DB_FORWARD_CHAT["accounts"]
DB_CATEGORIES = DB_FORWARD_CHAT["categories"]
DB_KEYWORD = DB_FORWARD_CHAT["keywords"]
DB_REPLACE_WORD = DB_FORWARD_CHAT["replace_words"]
DB_CRAWL = DB_FORWARD_CHAT["crawls"]
DB_POST = DB_FORWARD_CHAT["posts"]

DB_CATEGORIES.drop()
DB_ACCOUNT.drop()
DB_KEYWORD.drop()
DB_REPLACE_WORD.drop()
DB_CRAWL.drop()
DB_POST.drop()
mydict = { "id": str(uuid.uuid4().hex), "name": "84986626975", "task_id": str(CRAWL), "category_id": "52d8151df4f344bba4b5c56974213daa"}
DB_ACCOUNT.insert_one(mydict)

mydict = { "id": "52d8151df4f344bba4b5c56974213daa", "from": "https://t.me/CoinMarketCap", "type": "chanel", "category_id": "52d8151df4f344bba4b5c56974213daa",
            "category_keyword_id": "52d8151df4f344bba4b5c56974213dac", "category_post_id": "52d8151df4f344bba4b5c56974213dap",
            "category_replace_id": "52d8151df4f344bba4b5c56974213dar", "offset": 0}
DB_CRAWL.insert_one(mydict)
mydict = { "id": "52d8151df4f344bba4b5c56974213daa", "from": "https://t.me/Tojecoin2022", "type": "chanel", "category_id": "52d8151df4f344bba4b5c56974213daa",
            "category_keyword_id": "52d8151df4f344bba4b5c56974213dac", "category_post_id": "52d8151df4f344bba4b5c56974213dap",
            "category_replace_id": "52d8151df4f344bba4b5c56974213dar", "offset": 0}
DB_CRAWL.insert_one(mydict)


mydict = { "id": "52d8151df4f344bba4b5c56974213daa", "name": "coin", "type_id": "1", "cate_for": "account"}
DB_CATEGORIES.insert_one(mydict)
mydict = { "id": "52d8151df4f344bba4b5c56974213dap", "name": "bit coin", "type_id": "2", "cate_for": "account"}
DB_CATEGORIES.insert_one(mydict)
mydict = { "id": "52d8151df4f344bba4b5c56974213dac", "name": "Key Word", "type_id": "3", "cate_for": "filter"}
DB_CATEGORIES.insert_one(mydict)
mydict = { "id": "52d8151df4f344bba4b5c56974213dar", "name": "Replace", "type_id": "4", "cate_for": "filter"}
DB_CATEGORIES.insert_one(mydict)

mydict = { "id": str(uuid.uuid4().hex), "keyword": "keyword", "category_id": "52d8151df4f344bba4b5c56974213dac"}
DB_KEYWORD.insert_one(mydict)

mydict = { "id": str(uuid.uuid4().hex), "word": "keyword", "replace": "asaasda", "category_id": "52d8151df4f344bba4b5c56974213dar"}
DB_REPLACE_WORD.insert_one(mydict)

mydict = { "id": str(uuid.uuid4().hex), "post_to": "me",  "category_id": "52d8151df4f344bba4b5c56974213dap"}
DB_POST.insert_one(mydict)


db_task = DB_FORWARD_CHAT["tasks"]
db_task.insert_one({"id": str(CRAWL), "name": "Crawl", "cate_for": "account"})
db_task.insert_one({"id": str(POSTER), "name": "Post", "cate_for": "account"})
db_task.insert_one({"id": str(KEY_WORDS), "name": "Key Word", "cate_for": "filter"})
db_task.insert_one({"id": str(REPLACE_WORDS), "name": "Replace", "cate_for": "filter"})