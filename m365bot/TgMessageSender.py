from lib2to3.pytree import Base
import requests
import json

class TgMessageSender:

    def __init__(self, token) -> None:
        self.token = token
        self.sendMethodUrl = f"https://api.telegram.org/bot{self.token}/sendMessage"
        
    def sendMessage(self, message, urlButton, chatId):

        source_button = {
            'text': 'URL',
            'url': urlButton
        }

        keyboard = {
            'inline_keyboard': [[source_button]]
        }

        messageBody = {
            'text': message,
            'parse_mode': 'html',
            'chat_id': chatId,
            'reply_markup': json.dumps(keyboard)
        }

        messageJson = json.dumps(messageBody)

        try:
            response = requests.post(self.sendMethodUrl, messageBody)
            return response
        except BaseException as err:
            print(f'Error in sending to telegraph request. {err}')
            raise

        







    