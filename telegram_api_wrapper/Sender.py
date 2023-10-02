from urllib.parse import quote as urlencode
from typing import Optional

import requests

from Constants import BotChat

base_url = BotChat.BASE_URL.value


class Sender:

    @staticmethod
    def send_message(chat_id: str, message: str, disable_notification: Optional[bool] = False, parse_mode: Optional[str] = None) -> (
            requests.Response):
        message = urlencode(message)
        response = requests.get(
            f'{base_url}/sendMessage?chat_id={chat_id}&disable_notification={disable_notification}&parse_mode={parse_mode}&text={message}')
        return response

    @staticmethod
    def send_document(chat_id: str, document_path: str, caption: Optional[str] = None, disable_notification: Optional[bool] = True, parse_mode: Optional[str] = None) -> (
            requests.Response):
        with open(document_path, "rb") as document_path:
            payload = {
                "chat_id": chat_id,
                "caption": caption,
                "disable_notification": disable_notification,
                "parse_mode": parse_mode
            }
            response = requests.post(f"{base_url}/sendDocument", data=payload, files={"document": document_path})
        return response
