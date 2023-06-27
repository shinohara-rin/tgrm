from dotenv import load_dotenv
from telethon import TelegramClient, sync, events
from telethon.tl.functions.messages import SearchRequest
from telethon.tl.types import InputMessagesFilterEmpty
from os import getenv
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser(description="Telegram Message Deleter")
parser.add_argument('-G', '--gname', help='Group name')
parser.add_argument('-g', '--gid', type=int, help='Group ID')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

load_dotenv(override=True)

client = TelegramClient('tgrm', getenv('API_ID'), getenv(
    'API_HASH'), proxy=('socks5', '127.0.0.1', 1086))
client.start()

print("[+] Login successfully")

groups = filter(lambda dialog: dialog.is_group, client.get_dialogs())

if args.gname or args.gid:
    for group_chat in groups:
        if args.gname and group_chat.title == args.gname or args.gid and group_chat.id == args.gid:
            # Get my message count in the group
            sresult = client(SearchRequest(
                peer=group_chat.entity,
                q='',
                filter=InputMessagesFilterEmpty(),
                offset_id=0,
                add_offset=0,
                min_date=0,
                max_date=0,
                limit=0,
                max_id=0,
                min_id=0,
                hash=0,
                from_id=client.get_me().id
            ))
            message_count = sresult.count - 1  # not sure why this is needed, it just works

            # Print the message count and ask to confirm
            print(
                f"[!] You have {message_count} messages in {group_chat.title}, the last few are:")
            messages = client.iter_messages(
                group_chat.entity, limit=5, from_user='me')
            print('\n'.join([m.text for m in messages]))
            print(
                f"[!] Confirm deletion of messages in {group_chat.title}? (y/N)")
            if input() != 'y':
                print("[-] Aborted")
                exit()

            print(f"[+] Deleting messages in {group_chat.title}")

            # delete messages until empty
            with tqdm(total=message_count) as pbar:
                while True:
                    messages = client.iter_messages(
                        group_chat.entity, limit=100, from_user='me')
                    if pbar.n+1 >= message_count:
                        break
                    client.delete_messages(group_chat.entity, [
                                           m.id for m in messages])
                    pbar.update(100)


else:  # list groups
    print("[?] No group specified, listing all groups")
    for idx, group_chat in enumerate(groups):
        if str(group_chat.id).startswith('-100'):  # is group
            print(f'[{idx+1}] "{group_chat.title}": {group_chat.id}')
