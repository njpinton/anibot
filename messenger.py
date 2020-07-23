from config import ACCESS_TOKEN
from pymessenger.bot import Bot


ACCESS_TOKEN = ACCESS_TOKEN


class RandomAnimeBot:

    def __init__(self, recipientID, response, imageURL=None):
        self.recipientID = recipientID
        self.response = response
        self.imageURL = imageURL

    def send_message(self):
        bot = Bot(ACCESS_TOKEN)

        if self.imageURL:
            bot.send_image_url(self.recipientID, self.imageURL)

        bot.send_text_message(self.recipientID, self.response)

        return 'success'
