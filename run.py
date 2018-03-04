"""
Async and speedy web server that runs tweets nearby.
"""
import json
import asyncio

from urllib.parse import quote_plus

from sanic import Sanic
from sanic.config import Config
from sanic.response import file

from tweets_nearby import get_tweets
from tweets_nearby import get_tweets_map


app = Sanic(__name__)


@app.route('/')
async def index(request):
    """Render basic UI."""
    return await file('static/nearby_ui.html')


@app.route('/map')
async def map_ui(request):
    """Render the map."""
    return await file('static/nearby_map.html')


@app.route('/static/<name>')
async def static(request, name):
    """Render a static file."""
    return await file(f'static/{name}')


@app.websocket('/feed')
async def feed(request, ws):
    """Stream tweets via websockets to feed channel."""
    def parse_nearby(q_param):
        if 'geocode' not in q_param:
            where = q_param
        else:  # parse coordinates
            ge1, ge2 = tuple(map(float, q_param.lstrip('geocode:').split(',')))
            where = f'geocode:{ge1}, {ge2}'
        return quote_plus(where)

    while True:
        nearby = request.args.get('w') or 'me'
        lang = request.args.get('l') or 'en'
        basic_ui = not (request.args.get('on_map', 'false').lower() == 'true')
        where = parse_nearby(nearby)

        tweet_gen = get_tweets(where=where, lang=lang) if basic_ui else get_tweets_map(where=where, lang=lang)
        for tweet in tweet_gen:
            if not basic_ui:
                await ws.send(json.dumps(tweet))
                await asyncio.sleep(4)
            else:
                await ws.send(tweet)
                await asyncio.sleep(2)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=False)
