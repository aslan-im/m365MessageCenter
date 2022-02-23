import requests
import sys

class ErrorSender:
    def __init__(self, token, chatId) -> None:
        self.token = token
        self.sendMethodUrl = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.chatId = chatId
    
    def sendError(self, errorMessage):
        message = f"MessageCenterPy Error: {errorMessage}"
        messageBody = {
            'text': message,
            'parse_mode': 'html',
            'chat_id': self.chatId
        }
        
        try:
            response = requests.post(self.sendMethodUrl, messageBody)
            return response
        except BaseException as err:
            print(err)