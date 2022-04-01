try:
 import os, sys, random
 from time import sleep
 from telethon import TelegramClient, sync
 from telethon.errors import SessionPasswordNeededError, FloodWaitError
 from telethon.tl.functions.messages import  GetHistoryRequest
except:
 os.system("pip install random")
 os.system("pip install telethon")
 import os, sys, random
 from time import sleep
 from telethon import TelegramClient, sync
 from telethon.errors import SessionPasswordNeededError, FloodWaitError
 from telethon.tl.functions.messages import GetHistoryRequest
print("Chuyên Cung Cấp Telegram Và Hỗ trợ cách dịch vụ tele như kéo mem, Join Group,Chanel ae cần ib @Longsbkt") 
while True:
    
           
        phone = input("Nhap So Dien Thoai:")
        if phone == 'xx':
            os.system('clear')
            break
        else:
            api_id = 2015084
            api_hash = '24e8f34925604e25a9b8d695b21cf333'
            client = TelegramClient("session/"+phone,api_id,api_hash)
            client.connect()
            if not client.is_user_authorized():
                print (F"Session lỗi!" + phone)
                #client.log_out()
                client.disconnect()
                continue
            else:
                for message in client.get_messages(777000, limit=1):
                    msg = message.message
                    you_code = msg.split()[2].rstrip('.')
                    print ("Code =>> "+you_code)
                    client.disconnect()    
  