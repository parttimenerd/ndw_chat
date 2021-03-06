import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Union, Dict, Any

import yaml
from dataclasses_json import dataclass_json


def base_path() -> Path:
    return Path(os.getenv("NDW_HOME")) if os.getenv("NDW_HOME") else Path(__file__).parent.parent


@dataclass_json
@dataclass
class TrackConfig:
    name: str
    youtube_hash: str


@dataclass_json
@dataclass
class Config:

    port: int = 8080
    password: str = "test"
    length_limit: int = 200
    tracks: List[TrackConfig] = field(default_factory=lambda: [TrackConfig("room1", "stream url")])
    delete_after_days: float = 2
    host: str = "127.0.0.1"
    path: str = ""
    has_quiz: bool = False

_config: Optional[Config] = None
CONFIG_FILE = "config.yaml"


def config() -> Config:
    global _config
    config_file = base_path() / CONFIG_FILE
    if _config:
        return _config
    if config_file.exists():
        with config_file.open() as f:
            _config = Config.from_dict(yaml.safe_load(f))
            return _config
    else:
        with config_file.open("w") as f:
            yaml.dump(Config().to_dict(), f)
            print(f"Please update the template config file at {config_file}")
        exit(0)


def to_dict(val: Optional[Any]) -> Union[Dict, List, str, None]:
    if val is None or isinstance(val, list) or isinstance(val, dict) or isinstance(val, str):
        return val
    return val.to_dict()
