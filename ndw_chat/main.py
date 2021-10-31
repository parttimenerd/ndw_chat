"""
Based partly by https://stackoverflow.com/a/54908617
"""

import html
import json
import logging
from typing import List

import aiohttp_cors as aiohttp_cors
import coloredlogs as coloredlogs
from aiohttp.abc import Request

from ndw_chat.db import add_message, validate_track, set_state, get_messages, validate_message_id, \
    validate_state
from ndw_chat.util import config

coloredlogs.install()

from aiohttp import web
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


async def handle_get_messages(source: web.WebSocketResponse, arguments: dict):
    await source.send_json({msg.id: msg.to_dict() for msg in get_messages()})


SERVER_COMMANDS = {
    "set_state": handle_set_state,
    "set_content": handle_set_content,
    "get_messages": handle_get_messages
}


async def http_handler(request: Request):
    query = await request.json()
    track = query["track"]
    content = query["content"]
    if len(content) > config().length_limit:
        logging.info("Discard message that is too long")
        return web.Response(status=406)
    msg = add_message(validate_track(track), html.escape(content))
    logging.info(f"New message in {msg.track}: {msg.content}")
    await propagate("push_message", msg.to_dict())
    return web.Response(text="ok")


async def websocket_handler(request: Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    try:
        auth = await ws.receive()
        logging.info(f"Initial request {auth}")
        if auth["password"] == config().password:
            logging.info(f"Authentication successful")
        else:
            logging.error("Authentication unsuccessful")
            return
        authenticated_websockets.append(ws)
        async for msg in ws:
            parsed_msg = json.loads(msg)
            command = parsed_msg["command"]
            arguments = parsed_msg["arguments"]
            logging.info(f"Execute command {command} with arguments {arguments}")
            SERVER_COMMANDS[command](ws, arguments)
    except Exception as ex:
        logging.exception(ex)


def create_runner():
    app = web.Application()
    cors = aiohttp_cors.setup(app)
    routes = app.add_routes([
        web.post('/', http_handler),
        web.get('/ws', websocket_handler),
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
