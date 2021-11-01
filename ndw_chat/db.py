import enum
import time
from dataclasses import dataclass
from typing import Optional, List

from dataclasses_json import dataclass_json
from tinydb import TinyDB, Query
from tinydb.table import Document, Table

from ndw_chat.util import base_path, config


RAW = "raw"
VISIBLE = "visible"
ARCHIVED = "archived"


@dataclass_json
@dataclass
class Message:
    id: int
    track: str
    state: str
    time: float
    """ unix time at creation """
    content: str


_db: Optional[TinyDB] = None


def db(table: str) -> Table:
    global _db
    if not _db:
        _db = TinyDB(base_path() / "db.json")
        _db.table("host_messages")
        _db.table("messages")
    return _db.table(table)


def get_messages() -> List[Message]:
    return [Message.from_dict(msg) for msg in db("messages")]


def add_message(track: str, content: str) -> Message:
    msg = Message(len(db("messages")), track, RAW, time.time(), content)
    db("messages").insert(msg.to_dict())
    return msg


def set_state(id: int, new_state: str):
    db("messages").update({"state": new_state}, Query().id == id)


def set_content(id: int, content: str):
    db("messages").update({"content": content}, Query().id == id)


def get_host_message(track: str) -> str:
    val = db("host_messages").search(Query().track == track)
    if val:
        return val[0]["text"]
    return ""


def set_host_message(track: str, text: str):
    db("host_messages").upsert({"track": track, "text": text}, Query().track == track)


def get_tracks() -> List[str]:
    return [track.name for track in config().tracks]


class ValidationException(BaseException):
    pass


class UnknownTrack(ValidationException):
    pass


class UnknownMessage(ValidationException):
    pass


class UnknownState(ValidationException):
    pass


def validate_track(track: str) -> str:
    if not any(t.name == track for t in config().tracks):
        raise UnknownTrack()
    return track


def validate_message_id(id: int) -> int:
    if not db("messages").search(Query().id == id):
        raise UnknownMessage()
    return id


def validate_state(state: str) -> str:
    if state not in [RAW, VISIBLE, ARCHIVED]:
        raise UnknownState()
    return state
