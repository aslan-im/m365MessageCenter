from html_telegraph_poster import TelegraphPoster
import telepot
import sys

class MCMessage:
    def __init__(self, message_id):
        self.id = message_id
        self.title = "Unnamed"
        self.category = None
        self.tags = []
        self.published_time = None
        self.updated_time = None
        self.text = None
        self.external_link = None
        self.blog_link = None
        self.formatted_text = None
        self.telegraph_url = None

    def __format_message__(self):
        text = self.text
        simple_tags = (
            'span',
            'div',
            'h1',
            'h2',
            'div'
        )

        tags_to_remove = (
            '\&rarr',
            ' style=""',
            '&nbsp;',
            ' target\=\"_blank\"',
        )

        for tag in simple_tags:
            pattern = f"\<\/?{tag}\>"
            text.replace(pattern, '')

        for tag in tags_to_remove:
            text.replace(tag, '')

        return text

    def add_text(self, text):
        self.text = text
        self.formatted_text = self.__format_message__()

    def post_to_telegram(self, tg_token, chat_id):
        title = self.title
        message_id = self.id
        url = self.telegraph_url
        category = self.category
        pubDate = self.published_time
        updDate = self.updated_time

        tags = self.tags
        extLink = self.external_link
        blogLink = self.blog_link

        telegram_message = f"*{title}* \n[{message_id}]({url}) | {category} \nPublished: {pubDate} \nUpdated: {updDate} \n{tags}"
        if extLink and blogLink:
            telegram_message += f"\n[More details]({extLink}) \n[Blog]({blogLink})"
        elif extLink:
            telegram_message += f"\n[More details]({extLink})"
        elif blogLink:
            telegram_message += f"\n[Blog]({blogLink})"
        bot = telepot.Bot(tg_token)
        try:
            bot.sendMessage(chat_id=chat_id, parse_mode='markdown', text=telegram_message)
        except BaseException as err:
            print(err)
            raise


class Telegraph_To_MC:
    def get_tgph_token (self):
        self.telegraph = TelegraphPoster(use_api=True)
        token = self.telegraph.create_api_token('Microsoft 365 Message Center')
        return token


    def post_to_telegraph(self, messageTitle, messageId, messageText, ):
        response = self.telegraph.post(title=(messageTitle + ' | ' + messageId), text=messageText, author='@M365MessageCenter')
        return response['url']