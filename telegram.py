import random
import sys
import traceback

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
import csv
import time

api_id = "YOUR_ID"
api_hash = "YOUR_ID_HASH"
phone = "YOUR_NUMBER"
client = TelegramClient(phone, api_id, api_hash)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input("Enter the code: "))

users = []
with open("api.csv") as data_file:
    data = csv.reader(data_file)
    for row in data:
        user = {
            "username": row[0],
            "id": int(row[1]),
            "access_hash": row[2],
            "name": row[3],
        }
        users.append(user)

chats = []
last_date = None
chunk_size = 200
groups = []

result = client(
    GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0,
    )
)
chats.extend(result.chats)
for chat in chats:
    try:
        if chat.megagroup:
            groups.append(chat)
    except:
        continue

print("Choose a group to add members:")
i = 0
for group in groups:
    print(str(i) + "- " + group.title)
    i += 1
g_index = input("Enter a Number: ")
target_group = groups[int(g_index)]
target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)
mode = int(input("Enter 1 to add by username or 2 to add by ID: "))
n = 0

for user in users:
    n += 1
    if n % 50 == 0:
        time.sleep(900)
        try:
            print("Adding {}".format(user["id"]))
            if mode == 1:
                if user["username"] == "":
                    continue
                user_to_add = client.get_input_entity(user["username"])
            elif mode == 2:
                user_to_add = InputPeerUser(user["id"], user["access_hash"])
            else:
                sys.exit("Invalid Mode Selected. Please Try Again.")
            client(InviteToChannelRequest(target_group_entity, [user_to_add]))
            print("Waiting for 60-180 Seconds...")
            time.sleep(random.randrange(60, 180))
        except PeerFloodError:
            print(
                "Getting Flood Error from telegram. Script is stopping now. Please try again after some time."
            )
        except UserPrivacyRestrictedError:
            print("The user's privacy settings do not allow you to do this. Skipping.")
        except:
            traceback.print_exc()
            print("Unexpected Error")
            continue
