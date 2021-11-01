"""
Based partly by https://stackoverflow.com/a/54908617
"""

import html
import json
import logging
from typing import List, Any, Dict

import aiohttp_cors as aiohttp_cors
import coloredlogs as coloredlogs
from aiohttp.abc import Request

from ndw_chat.db import add_message, validate_track, set_state, get_messages, validate_message_id, \
    validate_state, set_host_message, get_host_message, get_tracks
from ndw_chat.util import config

coloredlogs.install()

from aiohttp import web, WSMsgType
import asyncio

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    )

authenticated_websockets: List[web.WebSocketResponse] = []


async def propagate(command: str, arguments: dict):
    global authenticated_websockets
    for websocket in authenticated_websockets:
        await websocket.send_json({"command": command, "arguments": arguments})


async def handle_set_state(source: web.WebSocketResponse, arguments: dict):
    set_state(validate_message_id(arguments["id"]), validate_state(arguments["state"]))
    await propagate("set_state", arguments)


async def handle_set_content(source: web.WebSocketResponse, arguments: dict):
    set_state(validate_message_id(arguments["id"]), arguments["content"])
    await propagate("set_content", arguments)


async def handle_set_host_message(source: web.WebSocketResponse, arguments: dict):
    set_host_message(arguments["track"], arguments["message"])
    await propagate("set_host_message", arguments)


SERVER_COMMANDS = {
    "set_state": handle_set_state,
    "set_content": handle_set_content,
    "set_host_message": handle_set_host_message
}


async def http_handler(request: Request):
    query = await request.json()
    track = query["track"]
    content = query["content"]
    if len(content) > config().length_limit and len(content) > 5:
        logging.info("Discard message that is too long")
        return web.Response(status=406)
    msg = add_message(validate_track(track), content)
    logging.info(f"New message in {msg.track}: {msg.content}")
    await propagate("push_message", msg.to_dict())
    return web.Response(text="ok")


def authenticated_request(func):
    """
    checks the query parameter 'password', the decorated function gets passed the query dict
    and returns a dict
    """
    async def wrapper(request: Request):
        query = request.query
        if "password" not in query or query["password"] != config().password:
            logging.error("Authentication unsuccessful")
            return web.Response(status=406)
        return web.Response(text=json.dumps(await func(query)),
                            content_type="application/json")
    return wrapper


def unauthenticated_request(func):
    """
    the decorated function gets passed the query dict and returns a dict
    """
    async def wrapper(request: Request):
        query = request.query
        return web.Response(text=json.dumps(await func(query)),
                            content_type="application/json")
    return wrapper


@authenticated_request
async def get_messages_handler(query: dict):
    return [msg.to_dict() for msg in sorted(get_messages(), key=lambda v: v.id)]


@authenticated_request
async def get_host_message_handler(query: dict):
    return {"message": get_host_message(track=query["track"])}


@unauthenticated_request
async def get_tracks_handler(query: dict):
    return {"tracks": get_tracks()}


async def websocket_handler(request: Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    try:
        msg = await ws.receive()
        logging.info(f"Initial request {msg}")
        if msg.type == WSMsgType.TEXT and json.loads(msg.data)["password"] == config().password:
            logging.info(f"Authentication successful")
        else:
            logging.error("Authentication unsuccessful")
            return
        authenticated_websockets.append(ws)

        while True:
            msg = await ws.receive()
            if (msg.type == WSMsgType.TEXT and msg.data == 'close') or msg.type == WSMsgType.CLOSE:
                await ws.close()
                logging.info("Closed connection")
                authenticated_websockets.remove(ws)
                return
            parsed_msg = json.loads(msg.data)
            command = parsed_msg["command"]
            arguments = parsed_msg["arguments"]
            logging.info(f"Execute command {command} with arguments {arguments}")
            try:
                await SERVER_COMMANDS[command](ws, arguments)
            except BaseException as ex:
                logging.exception(ex)
    except Exception as ex:
        logging.exception(ex)


def create_runner():
    app = web.Application()
    cors = aiohttp_cors.setup(app)
    routes = app.add_routes([
        web.post('/', http_handler),
        web.get('/ws', websocket_handler),
        web.get('/messages', get_messages_handler),
        web.get('/host_message', get_host_message_handler),
        web.get('/tracks', get_tracks_handler)
    ])
    for r in routes:
        cors.add(r, {"*": aiohttp_cors.ResourceOptions(allow_headers="*", allow_methods="*")})
    return web.AppRunner(app)


async def start_server(host="127.0.0.1"):
    runner = create_runner()
    await runner.setup()
    site = web.TCPSite(runner, host, config().port)
    await site.start()


def cli():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    loop.run_forever()


if __name__ == '__main__':
    cli()
