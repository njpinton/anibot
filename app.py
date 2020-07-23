import logging
from random import choice

from flask import Flask, request
from config import VERIFY_TOKEN
from jikanpy import Jikan

from messenger import RandomAnimeBot
from error import InvalidMethodError


app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


VERIFY_TOKEN = VERIFY_TOKEN
MAX_GENRE_COUNT = 43


@app.route('/', methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        token_sent = request.args.get('hub.verify_token')

        return verify_fb_token(token_sent)

    elif request.method == 'POST':
        output = request.get_json()

        for event in output['entry']:
            messaging = event['messaging']

            for message in messaging:

                if message.get('message'):
                    recipient_id = message['sender']['id']
                    response, img_url = get_message()

                    chatbot = RandomAnimeBot(recipient_id, response, img_url)
                    bot_message = chatbot.send_message()

        return 'message processed'

    else:
        raise InvalidMethodError('invalid choice of API method')


def verify_fb_token(tokenSent):
    if tokenSent == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    else:
        return 'invalid verification token'


def get_message():
        meta = get_random_from_100()

        title = meta['title']
        genres = meta['genres']
        image_url = meta['image_url']

        message = f'Title: {title}\nGenres: {', '.join(genres)}'

        return message, image_url


def get_random_from_100():
    jikan = Jikan()

    result = jikan.genre(type='anime', genre_id=choice(range(MAX_GENRE_COUNT)))
    anime_meta = result['anime'][choice(range(99))]
    genres = []

    for i in range(len(anime_meta['genres'])):
        genres.append(anime_meta['genres'][i]['name'])

    meta_data = dict(title=anime_meta['title'], genres=genres,
                     mal_id=anime_meta['mal_id'], url=anime_meta['url'],
                     synopsis=anime_meta['synopsis'],
                     image_url=anime_meta['image_url'],
                     score=anime_meta['score'], type=anime_meta['type'],
                     airing_start=anime_meta['airing_start'])

    return meta_data


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
