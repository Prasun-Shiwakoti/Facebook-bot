from fbchat import Client
from fbchat.models import *
import time
import random

BOT_ACTIVATE = "p! "
email = <your_facebook_email_id>
password = <your_facebook_password>
my_uid = 100011853588818
available_commands = ["roast"]

with open("roasts.txt", "r") as f:
    available_roasts = f.readlines()


class FacebookBot(Client):
    def __init__(self, email, password, session_cookies):
        super().__init__(email, password, user_agent=None, max_tries=5, session_cookies=session_cookies)
        self.available_commands = {"roast": self.roast}

    def onMessage(
            self,
            mid=None,
            author_id=None,
            message=None,
            message_object=None,
            thread_id=None,
            thread_type=ThreadType.USER,
            ts=None,
            metadata=None,
            msg=None,
    ):
        if thread_type == ThreadType.GROUP:
            rv = self.verify_group(thread_id)
            if rv[0]:
                message = str(message_object.text)
                if message.startswith(BOT_ACTIVATE):
                    return_message, command, mention_obj = self.clarify_request(message_object=message_object, group_object=rv[1])
                    if not return_message:
                        message_to_send = "Error: Couldn't identify the command. \nUsage: \np! <command> @mention \nAvailable commands: \nroast"
                    else:
                        message_to_send = self.available_commands[command](return_message)
                    print(message_to_send)
                    time.sleep(3)
                    send_message(message=message_to_send, target=rv[1], thread_type=ThreadType.GROUP, mention_obj=mention_obj)

    def verify_group(self, thread_id):
        group_obj = client.fetchGroupInfo(thread_id)[thread_id]
        if group_obj.name == "group 1":
            print("\ngroup verified")
            return True, group_obj
        return False, group_obj

    def clarify_request(self, message_object: Message, group_object):
        message = message_object.text
        message = message.replace(BOT_ACTIVATE, "")
        split_message = message.split(" ", maxsplit=1)
        command = split_message[0]
        if len(message_object.mentions) > 0:
            mention_object = message_object.mentions[0]
            mention = split_message[1][:mention_object.length]
        else:
            mention = ""
        return_message = f"<bot>: {mention.replace('@', '')}"

        if command.lower() in self.available_commands and mention:
            print("\nclarification done")
            mention_obj = Mention(thread_id=mention_object.thread_id, offset=7, length=mention_object.length - 1)
            return [return_message, command, mention_obj]
        else:
            return [None, None, None]

    def roast(self, message):
        roast_to_mentioned = random.choice(available_roasts)
        roast_message = f"{message}, {roast_to_mentioned}"
        return roast_message


def send_message(message, target, thread_type=ThreadType.USER, mention_obj: Mention = None):
    print("\nsending messages")
    sent = client.send(
        message=Message(text=message, mentions=[mention_obj]),
        thread_id=target.uid,
        thread_type=thread_type
    )
    if sent:
        print("Message sent successfully \n")
    else:
        print("Some error occurred \n")

print("logging in... \n")
client = FacebookBot(email=email, password=password)

client.listen(markAlive=True)

