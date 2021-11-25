"""
Based partly by https://stackoverflow.com/a/54908617
"""

import json
import logging
from typing import List, Dict, Callable

import aiohttp_cors as aiohttp_cors
import coloredlogs as coloredlogs
from aiohttp.abc import Request

import ndw_chat.quiz as quiz
from ndw_chat.db import add_message, validate_track, set_state, get_messages, validate_message_id, \
    validate_state, set_host_message, get_host_message, get_tracks, set_content, delete_old_messages
from ndw_chat.util import config, to_dict

coloredlogs.install()

from aiohttp import web, WSMsgType
import asyncio

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    )

authenticated_websockets: List[web.WebSocketResponse] = []


async def propagate(command: str, arguments: dict, receiver: web.WebSocketResponse = None):
    global authenticated_websockets
    for websocket in ([receiver] if receiver else authenticated_websockets):
        await websocket.send_json({"command": command, "arguments": arguments})


async def handle_set_state(source: web.WebSocketResponse, arguments: dict):
    set_state(validate_message_id(arguments["id"]), validate_state(arguments["state"]))
    await propagate("set_state", arguments)


async def handle_set_content(source: web.WebSocketResponse, arguments: dict):
    set_content(validate_message_id(arguments["id"]), arguments["content"])
    await propagate("set_content", arguments)


async def handle_set_host_message(source: web.WebSocketResponse, arguments: dict):
    set_host_message(arguments["track"], arguments["message"])
    await propagate("set_host_message", arguments)


async def handle_set_current_question(source: web.WebSocketResponse, query: dict):
    quiz.set_current_question(query["track"], query["question_id"])
    await propagate_current_question(query["track"])


async def handle_enable_current_question(source: web.WebSocketResponse, query: dict):
    quiz.enable_current_question(query["track"], bool(query["enabled"]))
    await propagate_current_question(query["track"])


SERVER_COMMANDS = {
    "set_state": handle_set_state,
    "set_content": handle_set_content,
    "set_host_message": handle_set_host_message,
    "set_current_question": handle_set_current_question,
    "enable_current_question": handle_enable_current_question
}


async def http_handler(request: Request):
    query = await request.json()
    track = query["track"]
    content = query["content"]
    if len(content) > config().length_limit or len(content) < 2:
        logging.info("Discard message that is too long")
        return web.Response(status=406)
    msg = add_message(validate_track(track), content)
    logging.info(f"New message in {msg.track}: {msg.content}")
    await propagate("push_message", msg.to_dict())
    return web.Response(text="ok")


HANDLERS: Dict[str, Callable] = {}


def register_handler(location: str):
    global HANDLERS

    def wrapper(func):
        assert location not in HANDLERS
        HANDLERS[location] = func
        return func

    return wrapper


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


@register_handler("messages")
@authenticated_request
async def get_messages_handler(query: dict):
    return [msg.to_dict() for msg in sorted(get_messages(), key=lambda v: v.id)]


@register_handler("host_message")
@authenticated_request
async def get_host_message_handler(query: dict):
    return {"message": get_host_message(track=query["track"])}


@register_handler("tracks")
@unauthenticated_request
async def get_tracks_handler(query: dict):
    return {"tracks": get_tracks()}


@register_handler("check_password")
@unauthenticated_request
async def get_check_password_handler(query: dict):
    return {"matches": config().password == query["password"]}


@register_handler("register_quiz_user")
@unauthenticated_request
async def register_quiz_user_handler(query: dict):
    user_id = quiz.register_user(query["pseudonym"], query["email"])
    return {"success": user_id is not None, "user_id": user_id}


@register_handler("user_registered")
@unauthenticated_request
async def user_registered_handler(query: dict):
    try:
        return {"registered": quiz.get_user(int(query["user_id"])) is not None}
    except:
        pass
    return {"registered": False}


@register_handler("submit_quiz_answer")
@unauthenticated_request
async def submit_quiz_answer_handler(query: dict):
    user_id = int(query["user_id"])
    question_id = int(query["question_id"])
    if quiz.answered(user_id, question_id):
        return {"success": False, "already_answered": True}
    answer = quiz.add_answer(user_id, question_id, query["answer"])
    await propagate("scores", quiz.user_scores().to_dict())
    return {"success": answer is not None, "already_answered": False}



@register_handler("unanswered_question")
@unauthenticated_request
async def get_unanswered_question_handler(query: dict):
    track = query["track"]
    cur_q = quiz.get_current_question(track)
    success_return = {"question": None}
    if not quiz.is_current_question_enabled(track):
        return {"question": None}
    if "user_id" in query:
        user_id = int(query["user_id"])
        if cur_q and not quiz.answered(user_id, cur_q.id):
            return {"question": cur_q.to_dict()}
        return {"question": None}
    else:
        return {"question": cur_q.to_dict()}


@register_handler("scores")
@authenticated_request
async def get_scores_handler(query: dict):
    return quiz.user_scores().to_dict()


def _get_current_question_dict(track: str):
    return {"current": to_dict(quiz.get_current_question(track)),
            "next": to_dict(quiz.get_next_question(track)),
            "prev": to_dict(quiz.get_prev_question(track)),
            "current_enabled": quiz.is_current_question_enabled(track)}


@register_handler("current_question")
@unauthenticated_request
async def get_current_question_handler(query: dict):
    return _get_current_question_dict(query["track"])


async def propagate_current_question(track: str, receiver=None):
    await propagate("set_current_question", {
        "track": track,
        "question": _get_current_question_dict(track)
    }, receiver)


@register_handler("has_quiz")
@unauthenticated_request
async def get_has_quiz_handler():
    return {"has_quiz": config().has_quiz}


async def propagate_initial_quiz_info(receiver: web.WebSocketResponse):
    if config().has_quiz:
        await propagate("scores", quiz.user_scores().to_dict(), receiver)
        for track_conf in config().tracks:
            await propagate_current_question(track_conf.name, receiver)
        await propagate("has_quiz", {"has_quiz": True}, receiver)


async def websocket_handler(request: Request):
    ws = web.WebSocketResponse(autoping=True, heartbeat=10000)
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
        try:
            await asyncio.sleep(0.02)
            await propagate_initial_quiz_info(ws)
        except:
            pass
        while True:
            msg = await ws.receive()
            if (msg.type == WSMsgType.TEXT and msg.data == 'close') or msg.type == WSMsgType.CLOSE:
                await ws.close()
                logging.info("Closed connection")
                authenticated_websockets.remove(ws)
                break
            if msg.type == WSMsgType.PING or str(msg.data) == '{"kind":"ping"}':
                await ws.pong(msg.data)
                continue
            if msg.type == WSMsgType.PONG:
                await ws.ping(msg.data)
                continue
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


def create_runner(path: str = ""):
    app = web.Application()
    cors = aiohttp_cors.setup(app)
    routes = app.add_routes([
                                web.post(path + '/send', http_handler),
                                web.get(path + '/ws', websocket_handler)
                            ] + [web.get(path + "/" + location, handler) for location, handler in HANDLERS.items()])
    for r in routes:
        cors.add(r, {"*": aiohttp_cors.ResourceOptions(allow_headers="*", allow_methods="*")})
    return web.AppRunner(app)


async def start_server(host="127.0.0.1"):
    runner = create_runner(config().path)
    await runner.setup()
    site = web.TCPSite(runner, host, config().port)
    await site.start()


async def delete_old_data():
    while True:
        delete_old_messages()
        quiz.delete_old_users_and_answers()
        await asyncio.sleep(100)


def cli():
    if config().has_quiz:
        quiz.quiz()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(start_server(config().host))
    loop.run_until_complete(delete_old_data())
    loop.run_forever()


if __name__ == '__main__':
    cli()
