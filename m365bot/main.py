#!/usr/bin/env python3
import os
import sys
import time
import dateutil.parser
from ErrorSender import ErrorSender
from datetime import datetime, timedelta
from SecretsManager import SecretsManager
from GraphApiRequests import GraphAPIRequests
from MCMessage import MCMessage, Telegraph_To_MC


def main():
    SECRETS_MANAGER_TOKEN = os.environ.get('SECRETS_MANAGER_TOKEN')
    if not SECRETS_MANAGER_TOKEN:
        print('Unable to get env variable SECRETS_MANAGER_TOKEN')
        sys.exit()

    secrets_manager = SecretsManager(SECRETS_MANAGER_TOKEN)
    try:
        config = secrets_manager.get_config()
    except BaseException as err:
        errorMessage = f"Was unable to get the config. {err}"
        print(errorMessage)
        sys.exit()      
        
    client_id = config['client_id']
    tenant_id = config['tenant_id']
    client_secret = config['client_secret']

    telegram_token = config['tg_token']
    prod_chat_id = config['tg_prod_chat_id']
    test_chat_id = config['test_chat_id']
    timedelta_minutes = config['time_delta']
    
    if config['running_mode'] == 'prod':
        chat_id = prod_chat_id
        print("Running in production mode")
    elif config['running_mode'] == 'test':
        chat_id = test_chat_id
        print("Running in test mode")
    else:
        print("Not correct mode has been set in config file. Possible values: 'prod' or 'test'. Test mode has been set as default")
        chat_id = test_chat_id
    
    telegramErrorsBotToken = config['tg_token_errors']
    errorsHandlerChatId = config['errors_handler_chat_id']
    errorSender = ErrorSender(telegramErrorsBotToken, errorsHandlerChatId)


    tokenIsInvalid = True
    tokenAttemptCounter = 0
    while tokenIsInvalid != False and tokenAttemptCounter < 10:
        tokenAttemptCounter += 1
        print(f"Getting Graph token. Attempt {tokenAttemptCounter}")
        graph_requester = GraphAPIRequests(client_id, tenant_id, client_secret)
        graph_requester.get_token()
        print("Token has been received")
        if ('error' not in graph_requester.token):
            tokenIsInvalid = False
        else:
            errorSender.sendError(f"Was unable to get Graph token. Attempt {tokenAttemptCounter}")

        time.sleep(3)

    current_datetime = datetime.utcnow()
    print(f"Current time: {current_datetime}")
    check_time = current_datetime - timedelta(minutes=timedelta_minutes)
    print(f"Check time: {check_time}")
    print("Getting MC messages")
    try:
        mc_messages = graph_requester.get_messages()
        print(f"Messages were received: {len(mc_messages)}")

    except KeyError as err:
        errorMessage = f"Was unable to get MC messages. {err}"
        print(errorMessage)
        errorSender.sendError(errorMessage)
        mc_messages = None

    except BaseException as err:
        errorMessage = f"Can't get MC messages. {err}"
        errorSender.sendError(errorMessage)
        print(errorMessage)


    if mc_messages != None:
        new_messages = []
        print("Working with new messages.")
        for message in mc_messages:
            message_date = dateutil.parser.parse(timestr=(message['lastModifiedDateTime']), ignoretz=True)
            # print(f"{message['id']}|{message_date}")
            if check_time < message_date < current_datetime:
                new_messages.append(message)

        print(f"New messages count: {len(new_messages)}")

        if new_messages:
            tgphSender = Telegraph_To_MC()
            tgph_token = tgphSender.get_tgph_token()

            if 'auth_url' in tgph_token:
                for new_message in new_messages:
                    print(f"Working with message {new_message['id']}")
                    message = MCMessage(new_message['id'])
                    message.add_text(str(new_message['body']['content']).replace('[', '<b>').replace(']', '</b>'))
                    message.title = new_message['title']
                    message.category = new_message['category']
                    tags = []
                    for tag in new_message['tags']:
                        tags.append('#' + tag.title().replace(' ', ''))
                    message.tags = ' '.join(tags)
                    published_time = new_message['startDateTime']
                    updated_time = new_message['lastModifiedDateTime']
                    message.published_time = dateutil.parser.parse(timestr=published_time, ignoretz=True).strftime("%Y-%m-%d")
                    message.updated_time = dateutil.parser.parse(timestr=updated_time, ignoretz=True).strftime("%Y-%m-%d")

                    message_external_link = next((details['value'] for details in new_message['details'] if details['name'] == 'ExternalLink' ), None)
                    if (message_external_link != None):
                        message.external_link = message_external_link

                    message_blog_link = next((details['value'] for details in new_message['details'] if details['name'] == 'BlogLink' ), None)
                    if(message_blog_link != None):
                        message.blog_link = message_blog_link

                    try:
                        message.telegraph_url = tgphSender.post_to_telegraph(message.title, message.id, message.formatted_text)
                        if message.telegraph_url == None:
                            raise sys.last_value

                    except BaseException as err:
                        errorMessage = f"Was unable to post to telegraph. Message ID: {message.id}. {err}"
                        errorSender.sendError(errorMessage)
                        print(errorMessage)

                    if message.telegraph_url != None:
                        try:
                            message.post_to_telegram(telegram_token, chat_id)
                        except BaseException as err:
                            errorMessage = f"Was unable to post to Telegram. Message ID: {message.id}. {err}"
                            print(errorMessage)
                            errorSender.sendError(errorMessage)

                    time.sleep(5)
        else:
            print("There are no new messages")

    print(f"Iteration has been completed. Going to the next in {timedelta_minutes} minutes")

if __name__ == "__main__":
    while True:
        main()
        time.sleep(1800)

