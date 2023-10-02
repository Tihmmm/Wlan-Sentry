from threading import Thread

import requests
from retry import retry

from Constants import BotChat, BotAllowedUser, SleepDuration, BotResponseMessage
from telegram_api_wrapper.Sender import Sender
from telegram_api_wrapper.CommanHandler import CommandHandler

base_url = BotChat.BASE_URL.value
user_id_allow_list = BotAllowedUser.list()


class Poller:

    def __init__(self, sender: Sender, command_handler: CommandHandler):
        self.sender = sender
        self.command_handler = command_handler

    @retry()
    def poll_for_messages(self):
        offset = "-1"
        while True:
            response = (requests.
                        get(f"{base_url}/getUpdates?offset={offset}&timeout={SleepDuration.BOT_POLL_TIMEOUT.value}")
                        .json())

            try:
                if not len(response["result"]) == 0:
                    user_id = str(response["result"][0]["message"]["from"]["id"])
                    command = response["result"][0]["message"]["text"].lower()

                    if user_id in user_id_allow_list:
                        self.sender.send_message(chat_id=user_id, message=BotResponseMessage.REQUEST_ACCEPTED.value)
                        bot_command_handler = Thread(target=self.command_handler.handle_command,
                                                     kwargs={"command": command, "user_id": user_id})
                        bot_command_handler.daemon = True
                        bot_command_handler.start()

                    offset = response["result"][0]["update_id"] + 1
            except KeyError:
                pass
            del response
