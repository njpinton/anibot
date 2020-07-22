import random
from jikanpy import Jikan
from flask import Flask, request
from pymessenger.bot import Bot
from config import ACCESS_TOKEN, VERIFY_TOKEN

app = Flask(__name__)
ACCESS_TOKEN = ACCESS_TOKEN
VERIFY_TOKEN = VERIFY_TOKEN
bot = Bot(ACCESS_TOKEN)

jikan = Jikan()
max_genre_count = 43


# https://test-bot-dot-netops-service-delivery.appspot.com
# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']

                    if message['message'].get('text'):
                        response_sent_text, img_url = get_message()
                        send_message(recipient_id, response_sent_text, img_url)
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        response_sent_nontext, img_url = get_message()
                        send_message(recipient_id, response_sent_nontext, img_url)
        return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


# chooses a random message to send to the user
def get_message():
    meta = get_random_from_100()
    title = meta['title']
    genres = meta['genres']
    # return selected item to the user
    return [f"Title: {title}\nGenres: {', '.join(genres)}", meta['image_url']]


def get_random_from_100():
    result = jikan.genre(type='anime', genre_id=random.choice(range(max_genre_count)))
    anime_meta = result['anime'][random.choice(range(99))]
    genres = []
    for i in range(len(anime_meta['genres'])):
        genres.append(anime_meta['genres'][i]['name'])

    meta_data = dict(title=anime_meta['title'],
                     genres=genres,
                     mal_id=anime_meta['mal_id'],
                     url=anime_meta['url'],
                     synopsis=anime_meta['synopsis'],
                     image_url=anime_meta['image_url'],
                     score=anime_meta['score'],
                     type=anime_meta['type'],
                     airing_start=anime_meta['airing_start'])
    return meta_data


# uses PyMessenger to send response to user
def send_message(recipient_id, response, img_url=None):
    # sends user the text message provided via input response parameter
    if img_url:
        bot.send_image_url(recipient_id, img_url)
        bot.send_text_message(recipient_id, response)
        return "success"
    bot.send_text_message(recipient_id, response)
    return "success"


if __name__ == "__main__":
    app.run()
